# azure_function/__init__.py

import logging
import azure.functions as func
import os
from utils import azure_storage, embeddings, summarizer
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Main entry point for the Azure Function
async def main(msg: func.ServiceBusMessage):
    """
    Azure Function triggered by a message from Azure Service Bus.

    Processes the geospatial data file associated with the task ID, generates embeddings,
    stores them in Pinecone, generates a summary, and caches the summary.

    Args:
        msg (func.ServiceBusMessage): The message received from the Service Bus queue.
    """
    # Retrieve task ID and file path from the message properties and body
    task_id = msg.application_properties.get("task_id")
    file_path = msg.get_body().decode("utf-8")
    logging.info(f"Processing task_id: {task_id}, file_path: {file_path}")
    try:
        # **Initial Status Update**: Mark task as "processing"
        await azure_storage.update_processing_status(task_id, "processing")
        logging.info(f"Task {task_id} status updated to 'processing'.")
        # Download the geospatial data file from Azure Blob Storage
        local_file_path = await azure_storage.download_file_from_blob(file_path)
        # Generate embeddings for the geospatial data
        embedding = embeddings.generate_embedding(local_file_path)

        # Store the embedding in the Pinecone index
        embeddings.store_embedding(task_id, embedding)
        # Generate a summary using LangChain and GPT-4
        summary = summarizer.generate_summary(task_id)
        # Cache the summary in Azure Redis Cache
        await azure_storage.cache_summary(task_id, summary)
        # Update the processing status to 'completed'
        await azure_storage.update_processing_status(task_id, "completed")
        logging.info(f"Task {task_id} completed successfully.")
    except Exception as e:
        logging.error(f"Task {task_id} failed with error: {str(e)}")
        # Update the processing status to 'failed'
        await azure_storage.update_processing_status(task_id, "failed")
