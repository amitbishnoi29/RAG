import weaviate
import logging
from typing import List, Dict, Any, Optional
from weaviate.classes.init import Auth
from weaviate.classes.query import MetadataQuery
from app.config import settings

logger = logging.getLogger(__name__)


class WeaviateClient:
    def __init__(self):
        self.client = None
        self.collection_name = "Documents"
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Weaviate client"""
        try:
            # Simple connection to localhost
            self.client = weaviate.connect_to_local(
                host="localhost",
                port=8080,
                skip_init_checks=True
            )
            
            self._create_collection_if_not_exists()
            logger.info("Weaviate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            raise

    def _create_collection_if_not_exists(self):
        """Create collection if it doesn't exist"""
        try:
            if not self.client.collections.exists(self.collection_name):
                self.client.collections.create(
                    name=self.collection_name,
                    properties=[
                        weaviate.classes.config.Property(
                            name="content",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="filename",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="chunk_index",
                            data_type=weaviate.classes.config.DataType.INT
                        ),
                        weaviate.classes.config.Property(
                            name="file_type",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="upload_date",
                            data_type=weaviate.classes.config.DataType.DATE
                        )
                    ],
                    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none()
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def add_documents(self, documents: List[Dict[str, Any]], vectors: List[List[float]]) -> List[str]:
        """Add documents with their embeddings to Weaviate"""
        try:
            collection = self.client.collections.get(self.collection_name)
            
            # Use individual insertions instead of batch to avoid GRPC
            uuids = []
            for doc, vector in zip(documents, vectors):
                # Filter out any reserved fields if they exist
                properties = {k: v for k, v in doc.items() if k not in ['id', 'vector']}
                
                # Insert each document individually using HTTP
                uuid = collection.data.insert(
                    properties=properties,
                    vector=vector
                )
                uuids.append(str(uuid))
            
            logger.info(f"Added {len(uuids)} documents to Weaviate")
            return uuids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def similarity_search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search"""
        try:
            collection = self.client.collections.get(self.collection_name)
            
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "content": item.properties.get("content", ""),
                    "metadata": {
                        "filename": item.properties.get("filename", ""),
                        "chunk_index": item.properties.get("chunk_index", 0),
                        "file_type": item.properties.get("file_type", ""),
                        "upload_date": item.properties.get("upload_date", ""),
                        "distance": item.metadata.distance if item.metadata else None
                    },
                    "score": 1 - (item.metadata.distance if item.metadata and item.metadata.distance else 0)
                })
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise

    def delete_all_documents(self):
        """Delete all documents from the collection"""
        try:
            collection = self.client.collections.get(self.collection_name)
            collection.data.delete_many()
            logger.info("Deleted all documents from collection")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise

    def get_document_count(self) -> int:
        """Get total number of documents in the collection"""
        try:
            collection = self.client.collections.get(self.collection_name)
            response = collection.aggregate.over_all(total_count=True)
            return response.total_count
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0

    def close(self):
        """Close the Weaviate client"""
        if self.client:
            self.client.close()


# Global instance
weaviate_client = WeaviateClient() 