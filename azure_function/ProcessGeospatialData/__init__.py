# azure_function/ProcessGeospatialData/__init__.py

import logging
import azure.functions as func
from ..utils import azure_storage, embeddings, summarizer
from dotenv import load_dotenv

load_dotenv()

# Main entry point for the Azure Function
async def main(msg: func.ServiceBusMessage):
    try:
        task_id = msg.application_properties.get("task_id")
        file_path = msg.get_body().decode("utf-8")
        logging.info(f"Processing task_id: {task_id}, file_path: {file_path}")

        # Initial Status Update
        await azure_storage.update_processing_status(task_id, "processing")

        # Download and Process File
        local_file_path = await azure_storage.download_file_from_blob(file_path)
        logging.info(f"File downloaded to {local_file_path}.")
        embedding = embeddings.generate_embedding(local_file_path)
        embeddings.store_embedding(task_id, embedding)

        # Generate Summary
        summary = summarizer.generate_summary(task_id)
        logging.info(f"Summary generated for task {task_id}: {summary}")
        await azure_storage.cache_summary(task_id, summary)
        await azure_storage.update_processing_status(task_id, "completed")
        logging.info(f"Task {task_id} completed successfully.")
    except Exception as e:
        logging.error(f"Task {task_id} failed with error: {str(e)}")
        await azure_storage.update_processing_status(task_id, "failed")
