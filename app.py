# app.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import uuid
import os
from dotenv import load_dotenv
from utils import azure_storage
import asyncio

app = FastAPI()

# Load environment variables
load_dotenv()

# Azure Service Bus Configuration
SERVICE_BUS_CONNECTION_STR = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME")

# Azure Blob Storage Configuration
CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")

# Initialize Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(conn_str=SERVICE_BUS_CONNECTION_STR, logging_enable=True)

@app.post("/submit_data")
async def submit_data(file: UploadFile = File(...)):
    if file.content_type not in ["application/octet-stream", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only geospatial datasets are allowed.")

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Upload the file to Azure Blob Storage
    file_path = f"{task_id}/{file.filename}"
    await azure_storage.upload_file_to_blob(file, file_path)

    # Send a message to Azure Service Bus
    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            message = ServiceBusMessage(body=file_path, application_properties={"task_id": task_id})
            await sender.send_messages(message)

    return {"status": "success", "data": {"task_id": task_id}}

@app.get("/get_summary/{task_id}")
async def get_summary(task_id: str):
    # Validate task ID format
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    # Check cache for summary
    summary = await azure_storage.get_summary_from_cache(task_id)
    if summary:
        return {"status": "success", "data": {"task_id": task_id, "summary": summary}}

    # If not in cache, check if processing is complete
    processing_status = await azure_storage.check_processing_status(task_id)
    if processing_status == "processing":
        return {"status": "success", "data": {"task_id": task_id, "status": "Processing"}}
    elif processing_status == "failed":
        raise HTTPException(status_code=500, detail="Processing failed.")
    else:
        raise HTTPException(status_code=404, detail="Task not found.")
