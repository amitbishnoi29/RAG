import logging
import os
from typing import List, Dict, Any
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain.schema import Document

from app.config import settings
from services.azure_openai_client import azure_openai_client
from services.weaviate_client import weaviate_client

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

    def load_document(self, file_path: str, file_type: str) -> List[Document]:
        """Load document using appropriate LangChain loader"""
        try:
            if file_type.lower() == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_type.lower() == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
            elif file_type.lower() in ['.txt', '.text']:
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} document pages from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split documents into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to split documents: {e}")
            raise

    def process_text_content(self, text_content: str, filename: str = "text_input") -> List[Document]:
        """Process raw text content into document chunks"""
        try:
            # Create a document from text content
            document = Document(
                page_content=text_content,
                metadata={"source": filename}
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([document])
            logger.info(f"Processed text content into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process text content: {e}")
            raise

    def ingest_document(self, file_path: str, filename: str = None) -> Dict[str, Any]:
        """Ingest a document file into the vector database"""
        try:
            if not filename:
                filename = os.path.basename(file_path)
            
            file_type = os.path.splitext(filename)[1]
            file_size = os.path.getsize(file_path)
            
            # Load and split document
            documents = self.load_document(file_path, file_type)
            chunks = self.split_documents(documents)
            
            # Prepare documents for vector storage
            chunk_texts = [chunk.page_content for chunk in chunks]
            
            # Create embeddings
            embeddings = azure_openai_client.create_embeddings(chunk_texts)
            
            # Prepare document objects for Weaviate
            weaviate_docs = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                weaviate_docs.append({
                    "content": chunk.page_content,
                    "filename": filename,
                    "chunk_index": i,
                    "file_type": file_type,
                    "upload_date": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # RFC3339 format
                })
            
            # Store in Weaviate
            document_ids = weaviate_client.add_documents(weaviate_docs, embeddings)
            
            result = {
                "success": True,
                "message": f"Successfully ingested {filename}",
                "filename": filename,
                "chunks_created": len(chunks),
                "file_size": file_size,
                "document_ids": document_ids
            }
            
            logger.info(f"Successfully ingested document: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to ingest document {filename}: {e}")
            return {
                "success": False,
                "message": f"Failed to ingest document: {str(e)}",
                "filename": filename,
                "chunks_created": 0
            }

    def ingest_text_content(self, text_content: str, filename: str = "text_input") -> Dict[str, Any]:
        """Ingest raw text content into the vector database"""
        try:
            # Process text into chunks
            chunks = self.process_text_content(text_content, filename)
            
            # Prepare documents for vector storage
            chunk_texts = [chunk.page_content for chunk in chunks]
            
            # Create embeddings
            embeddings = azure_openai_client.create_embeddings(chunk_texts)
            
            # Prepare document objects for Weaviate
            weaviate_docs = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                weaviate_docs.append({
                    "content": chunk.page_content,
                    "filename": filename,
                    "chunk_index": i,
                    "file_type": ".txt",
                    "upload_date": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # RFC3339 format
                })
            
            # Store in Weaviate
            document_ids = weaviate_client.add_documents(weaviate_docs, embeddings)
            
            result = {
                "success": True,
                "message": f"Successfully ingested text content",
                "filename": filename,
                "chunks_created": len(chunks),
                "document_ids": document_ids
            }
            
            logger.info(f"Successfully ingested text content: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to ingest text content: {e}")
            return {
                "success": False,
                "message": f"Failed to ingest text content: {str(e)}",
                "filename": filename,
                "chunks_created": 0
            }

    def retrieve_relevant_documents(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        try:
            if limit is None:
                limit = settings.max_retrieved_docs
            
            # Create query embedding
            query_embedding = azure_openai_client.create_embedding(query)
            
            # Perform similarity search
            results = weaviate_client.similarity_search(query_embedding, limit)
            
            logger.info(f"Retrieved {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant documents: {e}")
            raise


# Global instance
document_service = DocumentService() 