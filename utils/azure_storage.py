# utils/azure_storage.py

import os
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
import aioredis
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")

# Azure Redis Cache Configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Initialize the Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

async def upload_file_to_blob(file, file_path):
    """
    Uploads a file to Azure Blob Storage.

    Args:
        file (UploadFile): The file object to upload.
        file_path (str): The path in the blob storage where the file will be stored.
    """
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_path)
    content_settings = ContentSettings(content_type=file.content_type)
    data = await file.read()
    await blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)

async def download_file_from_blob(file_path):
    """
    Downloads a file from Azure Blob Storage to a local temporary directory.

    Args:
        file_path (str): The path in the blob storage where the file is stored.

    Returns:
        str: The local file path where the file has been downloaded.
    """
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_path)
    download_file_path = f"/tmp/{os.path.basename(file_path)}"

    # Ensure the /tmp directory exists
    os.makedirs("/tmp", exist_ok=True)

    with open(download_file_path, "wb") as download_file:
        download_stream = await blob_client.download_blob()
        data = await download_stream.readall()
        download_file.write(data)

    return download_file_path

async def cache_summary(task_id, summary):
    """
    Caches the summary text in Azure Redis Cache with the associated task ID.

    Args:
        task_id (str): The unique identifier for the task.
        summary (str): The summary text to cache.
    """
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD, encoding='utf-8'
    )
    await redis.set(f"summary:{task_id}", summary)
    redis.close()
    await redis.wait_closed()

async def get_summary_from_cache(task_id):
    """
    Retrieves the cached summary text from Azure Redis Cache.

    Args:
        task_id (str): The unique identifier for the task.

    Returns:
        str or None: The cached summary text, or None if not found.
    """
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD, encoding='utf-8'
    )
    summary = await redis.get(f"summary:{task_id}")
    redis.close()
    await redis.wait_closed()
    return summary

async def update_processing_status(task_id, status):
    """
    Updates the processing status of a task in Azure Redis Cache.

    Args:
        task_id (str): The unique identifier for the task.
        status (str): The processing status ('processing', 'completed', 'failed').
    """
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD, encoding='utf-8'
    )
    await redis.set(f"status:{task_id}", status)
    redis.close()
    await redis.wait_closed()

async def check_processing_status(task_id):
    """
    Checks the processing status of a task from Azure Redis Cache.

    Args:
        task_id (str): The unique identifier for the task.

    Returns:
        str or None: The processing status, or None if not found.
    """
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD, encoding='utf-8'
    )
    status = await redis.get(f"status:{task_id}")
    redis.close()
    await redis.wait_closed()
    return status
