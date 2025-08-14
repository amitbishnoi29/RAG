import logging
from typing import List, Dict, Any, AsyncGenerator
from openai import AzureOpenAI
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        try:
            response = self.client.embeddings.create(
                model=settings.azure_openai_embedding_deployment,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Created {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        return self.create_embeddings([text])[0]

    async def chat_completion_stream(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """Create streaming chat completion"""
        try:
            logger.info("Starting streaming chat completion")
            
            # Create the streaming response
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            chunk_count = 0
            # Process each chunk immediately as it arrives
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        chunk_count += 1
                        logger.debug(f"Streaming chunk #{chunk_count}: '{content}'")
                        yield content
                        
                        # Yield control back to the event loop to ensure real streaming
                        await asyncio.sleep(0)
                    
            logger.info(f"Streaming completed with {chunk_count} chunks")
                    
        except Exception as e:
            logger.error(f"Failed to create streaming chat completion: {e}")
            raise

    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Create non-streaming chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            else:
                logger.warning("No choices returned from Azure OpenAI")
                return "No response generated"
            
        except Exception as e:
            logger.error(f"Failed to create chat completion: {e}")
            raise

    def create_rag_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Create RAG prompt with context documents"""
        context_text = "\n\n".join([
            f"Document: {doc['metadata']['filename']}\nContent: {doc['content']}"
            for doc in context_docs
        ])
        
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context. 
        Use the context documents to answer the user's question. If the answer cannot be found in the context, 
        say so clearly. Always cite the source documents when possible."""
        
        user_prompt = f"""Context Documents:
{context_text}

User Question: {query}

Please provide a helpful answer based on the context above."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


# Global instance
azure_openai_client = AzureOpenAIClient() 