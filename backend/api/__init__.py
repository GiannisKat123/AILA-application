"""
The `api` package defines the backend’s HTTP and WebSocket interface,
along with supporting utilities and data models.

It integrates FastAPI routing, JWT authentication, and the LLM pipeline
for legal Q&A. The package ensures clean request/response validation,
secure access control, and orchestration of the pipeline workflow.

Contents
--------
- fast_api
    Defines the FastAPI router with endpoints for:
        * User login, registration, verification, and logout
        * Conversation creation, update, and retrieval
        * Messaging and feedback submission
        * Chat endpoint that streams responses from the LLM pipeline

- models
    Pydantic schemas for request/response validation:
        * User credentials, registration, and verification
        * Conversation and message payloads
        * Authentication responses and feedback objects

- utils
    JWT utilities:
        * `create_access_token` — issues signed JWTs with expiration
        * `verify_token` — validates JWTs and extracts user identity

- llm_pipeline
    Orchestration of the LangGraph-based RAG workflow:
        * Loads vector indexes and reranker models
        * Provides classification, retrieval, summarization, and web search
        * Executes the full multilingual legal Q&A pipeline

"""
