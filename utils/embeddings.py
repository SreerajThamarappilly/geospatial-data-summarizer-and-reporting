# utils/embeddings.py

import os
import openai
import pinecone

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "geospatial-embeddings"

openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
if INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(INDEX_NAME, dimension=1536)  # Assuming OpenAI's embedding size

index = pinecone.Index(INDEX_NAME)

def generate_embedding(file_path):
    # Read file content
    with open(file_path, 'rb') as f:
        content = f.read()

    # For simplicity, we'll assume the content is text-based metadata
    # In practice, you might extract metadata or textual representation
    text_representation = extract_text_from_geospatial_data(content)

    # Generate embedding
    response = openai.Embedding.create(
        input=text_representation,
        model="text-embedding-ada-002"
    )
    embedding = response['data'][0]['embedding']
    return embedding

def store_embedding(task_id, embedding):
    index.upsert([(task_id, embedding)])

def extract_text_from_geospatial_data(content):
    # Placeholder function to extract text from geospatial data
    return "Extracted textual representation of geospatial data."
