# utils/azure_storage.py

import os
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
import aioredis

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

async def upload_file_to_blob(file, file_path):
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_path)
    content_settings = ContentSettings(content_type=file.content_type)
    data = await file.read()
    await blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)

async def download_file_from_blob(file_path):
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_path)
    download_file_path = f"/tmp/{os.path.basename(file_path)}"
    with open(download_file_path, "wb") as download_file:
        download_stream = await blob_client.download_blob()
        data = await download_stream.readall()
        download_file.write(data)
    return download_file_path

async def cache_summary(task_id, summary):
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD)
    await redis.set(f"summary:{task_id}", summary)
    redis.close()
    await redis.wait_closed()

async def get_summary_from_cache(task_id):
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD)
    summary = await redis.get(f"summary:{task_id}", encoding='utf-8')
    redis.close()
    await redis.wait_closed()
    return summary

async def update_processing_status(task_id, status):
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD)
    await redis.set(f"status:{task_id}", status)
    redis.close()
    await redis.wait_closed()

async def check_processing_status(task_id):
    redis = await aioredis.create_redis_pool(
        (REDIS_HOST, int(REDIS_PORT)), password=REDIS_PASSWORD)
    status = await redis.get(f"status:{task_id}", encoding='utf-8')
    redis.close()
    await redis.wait_closed()
    return status
