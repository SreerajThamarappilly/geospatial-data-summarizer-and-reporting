# app.py

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import uuid
import os
from dotenv import load_dotenv
from azure_function.utils import azure_storage

# Initialize FastAPI application
app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Azure Service Bus Configuration
SERVICE_BUS_CONNECTION_STR = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME")

# Initialize Service Bus Client (asynchronous)
servicebus_client = ServiceBusClient.from_connection_string(
    conn_str=SERVICE_BUS_CONNECTION_STR, logging_enable=True
)

@app.post("/submit_data", status_code=status.HTTP_202_ACCEPTED)
async def submit_data(file: UploadFile = File(...)):
    """
    Endpoint to submit geospatial data for processing.

    Args:
        file (UploadFile): The uploaded geospatial data file.

    Returns:
        JSONResponse: A response containing the task ID.
    """
    # Validate file type
    if file.content_type not in ["application/octet-stream", "image/tiff"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only geospatial datasets are allowed."
        )

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Define the file path in Azure Blob Storage
    file_path = f"{task_id}/{file.filename}"

    # Upload the file to Azure Blob Storage
    await azure_storage.upload_file_to_blob(file, file_path)

    # Send a message to Azure Service Bus for asynchronous processing
    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            message = ServiceBusMessage(
                body=file_path,
                application_properties={"task_id": task_id}
            )
            await sender.send_messages(message)

    # Return a response with the task ID
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"status": "success", "data": {"task_id": task_id}}
    )

@app.get("/get_summary/{task_id}")
async def get_summary(task_id: str):
    """
    Endpoint to retrieve the summary of the processed geospatial data.

    Args:
        task_id (str): The unique identifier for the processing task.

    Returns:
        JSONResponse: A response containing the summary or status of the task.
    """
    # Validate task ID format
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format."
        )

    # Check if the summary is available in cache
    summary = await azure_storage.get_summary_from_cache(task_id)
    if summary:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "data": {"task_id": task_id, "summary": summary}}
        )

    # Check the processing status of the task
    processing_status = await azure_storage.check_processing_status(task_id)
    if processing_status == "processing":
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"status": "processing", "data": {"task_id": task_id, "status": "Processing"}}
        )
    elif processing_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Processing failed."
        )
    else:
        # Task ID not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Endpoint to fetch task progress and status.

    Args:
        task_id (str): The unique identifier for the processing task.

    Returns:
        JSONResponse: A response containing the summary or status of the task.
    """
    status = redis_client.get(f"task_status:{task_id}")
    if status:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"status": status, "data": {"task_id": task_id, "status": "Processing"}}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "not found", "data": "Task not found."}
        )
