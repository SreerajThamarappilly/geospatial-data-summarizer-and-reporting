# utils/summarizer.py

import os
import openai
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
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
index = pinecone.Index(INDEX_NAME)

def generate_summary(task_id):
    # Retrieve embedding
    query_embedding = index.fetch(ids=[task_id])['vectors'][task_id]['values']

    # Query similar embeddings
    results = index.query(queries=[query_embedding], top_k=5)

    # Retrieve relevant data
    relevant_texts = retrieve_relevant_texts(results)

    # Generate summary using LangChain
    llm = OpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)
    prompt_template = PromptTemplate(
        input_variables=["context"],
        template="Summarize the following geospatial data:\n\n{context}\n\nSummary:"
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    summary = chain.run(context=relevant_texts)
    return summary

def retrieve_relevant_texts(results):
    # Placeholder function to retrieve texts based on query results
    return "Consolidated relevant geospatial data for summarization."
