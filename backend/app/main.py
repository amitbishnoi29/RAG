import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import uvicorn
import os
import tempfile
import json

from app.config import settings
from models.schemas import (
    ChatRequest, ChatResponse, IngestRequest, IngestResponse,
    ErrorResponse
)
from services.document_service import document_service
from services.azure_openai_client import azure_openai_client
from services.weaviate_client import weaviate_client
from app.heygen_routes import router as heygen_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG Chatbot with Voice using Azure OpenAI + Weaviate"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HeyGen routes
app.include_router(heygen_router, prefix="/api", tags=["heygen"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Chatbot API",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Weaviate connection
        doc_count = weaviate_client.get_document_count()
        
        return {
            "status": "healthy",
            "weaviate_connected": True,
            "documents_count": doc_count,
            "version": settings.app_version
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(request: IngestRequest):
    """Ingest text content into the knowledge base"""
    try:
        if not request.text_content:
            raise HTTPException(status_code=400, detail="Text content is required")
        
        filename = request.filename or "text_input"
        result = document_service.ingest_text_content(
            text_content=request.text_content,
            filename=filename
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return IngestResponse(
            success=True,
            message=result["message"],
            document_id=result.get("document_ids", [None])[0] if result.get("document_ids") else None,
            chunks_created=result["chunks_created"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest text: {str(e)}")


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    """Ingest file into the knowledge base"""
    try:
        # Check file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed types: {settings.allowed_file_types}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Ingest the document
            result = document_service.ingest_document(
                file_path=temp_file_path,
                filename=file.filename
            )
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return IngestResponse(
                success=True,
                message=result["message"],
                document_id=result.get("document_ids", [None])[0] if result.get("document_ids") else None,
                chunks_created=result["chunks_created"]
            )
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {str(e)}")


@app.post("/chat")
async def chat_stream(request: ChatRequest):
    """Chat endpoint with streaming response"""
    try:
        # Retrieve relevant documents
        relevant_docs = document_service.retrieve_relevant_documents(request.message)
        
        # Create RAG prompt
        messages = azure_openai_client.create_rag_prompt(request.message, relevant_docs)
        
        # Add conversation history if provided
        if request.conversation_history:
            # Insert conversation history before the current query
            history_messages = []
            for msg in request.conversation_history[-10:]:  # Limit to last 10 messages
                history_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Combine system prompt, history, and current query
            messages = [messages[0]] + history_messages + [messages[1]]
        
        if request.stream:
            # Streaming response
            async def generate_response():
                try:
                    logger.info("🌊 Starting SSE response generation")
                    response_data = {
                        "sources": [doc["metadata"]["filename"] for doc in relevant_docs]
                    }
                    logger.info("📚 Sending sources")
                    yield f"data: {json.dumps(response_data)}\n\n"
                    
                    chunk_count = 0
                    async for chunk in azure_openai_client.chat_completion_stream(
                        messages=messages,
                        temperature=settings.temperature,
                        max_tokens=settings.max_tokens
                    ):
                        chunk_count += 1
                        logger.info(f"📝 SSE: Sending chunk #{chunk_count}: '{chunk}'")
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    
                    logger.info(f"✅ SSE: Completed with {chunk_count} chunks")
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    logger.error(f"Error in streaming response: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_response(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # Non-streaming response
            response_content = azure_openai_client.chat_completion(
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            return ChatResponse(
                response=response_content,
                sources=[doc["metadata"]["filename"] for doc in relevant_docs]
            )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.delete("/documents")
async def clear_documents():
    """Clear all documents from the knowledge base"""
    try:
        weaviate_client.delete_all_documents()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear documents: {str(e)}")


@app.get("/documents/count")
async def get_document_count():
    """Get the number of documents in the knowledge base"""
    try:
        count = weaviate_client.get_document_count()
        return {"count": count}
    except Exception as e:
        logger.error(f"Failed to get document count: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document count: {str(e)}")


@app.post("/test/azure-openai")
async def test_azure_openai(request: dict):
    """Test Azure OpenAI connectivity with a simple message"""
    try:
        test_message = request.get("message", "Hello, this is a test message. Please respond with 'Azure OpenAI is working correctly!'")
        
        # Test chat completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond exactly as requested."},
            {"role": "user", "content": test_message}
        ]
        
        response = azure_openai_client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=100
        )
        
        # Test embedding creation
        test_embedding = azure_openai_client.create_embeddings([test_message])
        
        return {
            "status": "success",
            "azure_openai_chat_response": response,
            "embedding_dimensions": len(test_embedding[0]) if test_embedding else 0,
            "test_message": test_message
        }
        
    except Exception as e:
        logger.error(f"Azure OpenAI test failed: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "test_message": request.get("message", "Hello, this is a test message.")
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 