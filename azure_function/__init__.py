# azure_function/__init__.py

import logging
import azure.functions as func
import os
from utils import azure_storage, embeddings, summarizer
import asyncio

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

async def main(msg: func.ServiceBusMessage):
    task_id = msg.application_properties.get("task_id")
    file_path = msg.get_body().decode("utf-8")

    logging.info(f"Processing task_id: {task_id}, file_path: {file_path}")

    try:
        # Download file from Blob Storage
        local_file_path = await azure_storage.download_file_from_blob(file_path)

        # Generate embeddings
        embedding = embeddings.generate_embedding(local_file_path)

        # Store embeddings in Pinecone
        embeddings.store_embedding(task_id, embedding)

        # Generate summary using LangChain and GPT-4
        summary = summarizer.generate_summary(task_id)

        # Cache the summary
        await azure_storage.cache_summary(task_id, summary)

        # Update processing status
        await azure_storage.update_processing_status(task_id, "completed")

        logging.info(f"Task {task_id} completed successfully.")

    except Exception as e:
        logging.error(f"Task {task_id} failed with error: {str(e)}")
        # Update processing status
        await azure_storage.update_processing_status(task_id, "failed")
