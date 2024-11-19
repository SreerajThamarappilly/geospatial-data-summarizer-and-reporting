# utils/summarizer.py

import os
import openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
import pinecone
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
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_REGION)

# Connect to the existing index
index = pc.Index(host=PINECONE_INDEX_NAME)

def generate_summary(task_id):
    """
    Generates a summary for the geospatial data associated with the given task ID.

    Args:
        task_id (str): The unique identifier for the task.

    Returns:
        str: The generated summary text.
    """
    # Retrieve the embedding vector for the given task ID
    response = index.fetch(ids=[task_id])
    if task_id in response['vectors']:
        query_embedding = response['vectors'][task_id]['values']
    else:
        raise ValueError(f"No embedding found for task ID: {task_id}")

    # Query similar embeddings in the Pinecone index
    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_values=False,
        include_metadata=False
    )

    # Retrieve relevant texts based on the query results
    relevant_texts = retrieve_relevant_texts(results)

    # Initialize the OpenAI LLM via LangChain
    llm = OpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)

    # Define a prompt template for summarization
    prompt_template = PromptTemplate(
        input_variables=["context"],
        template="Summarize the following geospatial data:\n\n{context}\n\nSummary:"
    )

    # Create an LLM chain with the language model and prompt
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Generate the summary by running the chain with the relevant texts
    summary = chain.run(context=relevant_texts)

    return summary

def retrieve_relevant_texts(results):
    """
    Retrieves relevant textual data based on the query results from Pinecone.

    Args:
        results (dict): The query results containing IDs of similar embeddings.

    Returns:
        str: A concatenated string of relevant texts for summarization.
    """
    # Placeholder implementation
    # In practice, fetch the actual texts associated with the result IDs
    relevant_texts = []

    # Iterate over the matched results
    for match in results['matches']:
        matched_task_id = match['id']
        # Retrieve the text representation associated with the matched_task_id
        # For now, we will use a placeholder text
        text = f"Text representation for task ID {matched_task_id}."
        relevant_texts.append(text)

    # Concatenate all relevant texts into a single string
    combined_text = "\n\n".join(relevant_texts)
    return combined_text
