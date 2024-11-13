# geospatial-data-summarizer-and-reporting

An advanced application that processes drone datasets to generate comprehensive summaries and reports. It leverages Retrieval Augmented Generation (RAG), LangChain, and vector databases to efficiently retrieve relevant data and produce human-readable summaries. It supports various geospatial data types such as DSM, DTM, and multiband Orthophotos.

## Architecture Overview

The application uses a microservices architecture with the following components:

- **FastAPI Application**: Provides RESTful API endpoints for data submission and retrieval.
- **Azure Blob Storage**: Stores large geospatial datasets.
- **Azure Service Bus**: Acts as a message broker for asynchronous task processing.
- **Azure Functions**: Processes geospatial data asynchronously.
- **Pinecone Vector Database**: Stores vector embeddings of geospatial data for efficient retrieval.
- **LangChain**: Orchestrates data retrieval and language generation using OpenAI.
- **Azure Cache for Redis**: Caches summaries for quick retrieval.
- **Azure Cognitive Services**: Provides additional AI capabilities if needed.

## Technologies and Concepts Used

- **Python 3.11**
- **FastAPI**: For building the API layer.
- **Azure Services**: Blob Storage, Service Bus, Functions, Cache for Redis.
- **Pinecone**: Vector database for storing embeddings.
- **LangChain**: Framework for building language model applications.
- **OpenAI**: For generating summaries.
- **Retrieval Augmented Generation (RAG)**: Combines retrieval of data with generation capabilities.
- **Docker**: Containerization of the application.
- **OOP Principles and Design Patterns**: Applied throughout the codebase for maintainability and scalability.

## Directory Structure

```bash
geospatial_summarizer/
├── app.py
├── azure_function/
│   └── __init__.py
├── utils/
│   ├── __init__.py
│   ├── azure_storage.py
│   ├── embeddings.py
│   └── summarizer.py
├── .env
├── requirements.txt
└── README.md
```

- **Object-Oriented Principles**:
    - Utilities are organized into modules (utils package) with clear responsibilities.
    - Functions are modular, promoting reusability and maintainability.

- **Design Patterns**:
    - Factory Pattern: Used in initializing clients for services like Azure Blob Storage and Pinecone.
    - Asynchronous Programming: Utilizes async and await for non-blocking I/O operations.

- **Advanced Concepts**:
    - Dependency Injection: Environment variables are loaded and injected where needed.
    - Exception Handling: Comprehensive error handling to ensure robustness.

## Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
AZURE_SERVICE_BUS_CONNECTION_STRING=your_service_bus_connection_string
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
```

## License

*This project is proprietary and is the confidential property. All rights reserved. Do not distribute or disclose this code without proper authorization.*
