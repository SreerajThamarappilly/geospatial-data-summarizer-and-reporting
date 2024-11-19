# utils/embeddings.py

import os
import openai
from pinecone import Pinecone
import rasterio
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve API keys and other configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "geospatial-embeddings"  # Name of the Pinecone index
PINECONE_REGION = os.getenv("PINECONE_REGION")  # e.g., "us-east-1-aws" or "us-west1-gcp"

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize the Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists and create it if it doesn't
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,
        metric='euclidean',
        pod_type='s1',
        pods=1,
        replicas=1,
        metadata_config={'indexed': []}
    )

# Access the index
index = pc.Index(host=PINECONE_INDEX_NAME)

def generate_embedding(file_path):
    """
    Generates an embedding vector for the given geospatial data file.

    Args:
        file_path (str): The local file path to the geospatial data.

    Returns:
        list: The embedding vector representing the geospatial data.
    """
    # Read file content
    with open(file_path, 'rb') as f:
        content = f.read()

    # Extract textual representation from the geospatial data
    # This function should be implemented to parse actual geospatial data
    text_representation = extract_text_from_geospatial_data(content)

    # Generate embedding using OpenAI's Embedding API
    response = openai.Embedding.create(
        input=text_representation,
        model="text-embedding-ada-002"
    )

    # Extract the embedding vector from the API response
    embedding = response['data'][0]['embedding']
    return embedding

def store_embedding(task_id, embedding):
    """
    Stores the embedding vector in the Pinecone index with the associated task ID.

    Args:
        task_id (str): The unique identifier for the task.
        embedding (list): The embedding vector to store.
    """
    # Prepare the data for upsert
    upsert_data = [Vector(id=task_id, values=embedding)]

    # Upsert the embedding into the Pinecone index
    index.upsert(vectors=upsert_data)

def extract_text_from_geospatial_data(content):
    """
    Extracts a textual representation from geospatial data content.

    Args:
        content (bytes): The raw content of the geospatial data file.

    Returns:
        str: The extracted textual representation of the geospatial data.
    """
    with rasterio.MemoryFile(content) as memfile:
        with memfile.open() as dataset:
            # Extract metadata
            metadata = dataset.meta
            description = dataset.descriptions
            # Combine metadata into a text representation
            text_representation = f"Metadata: {metadata}, Descriptions: {description}"
            return text_representation

def query_similar_embeddings(task_id, top_k=5):
    """
    Queries the Pinecone index for embeddings similar to the one associated with the given task ID.

    Args:
        task_id (str): The unique identifier for the task.
        top_k (int): The number of similar embeddings to retrieve.

    Returns:
        list: A list of IDs and scores of similar embeddings.
    """
    # Fetch the embedding vector for the given task ID
    response = index.fetch(ids=[task_id])
    if task_id in response['vectors']:
        query_embedding = response['vectors'][task_id]['values']

        # Perform similarity search in the index
        search_response = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_values=False,
            include_metadata=False
        )

        # Return the IDs of similar embeddings
        return search_response['matches']
    else:
        return []

def delete_embedding(task_id):
    """
    Deletes the embedding associated with the given task ID from the Pinecone index.

    Args:
        task_id (str): The unique identifier for the task.
    """
    index.delete(ids=[task_id])
