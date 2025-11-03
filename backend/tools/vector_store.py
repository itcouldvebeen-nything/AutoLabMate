"""
Vector Store - RAG integration
Interface for storing and retrieving experiment context
Supports Pinecone and mock implementation
"""

import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector Store for RAG-based context retrieval
    
    Stores experimental metadata, SOPs, and historical analysis patterns
    """
    
    def __init__(self):
        """Initialize Vector Store"""
        self.use_mock = os.getenv("MOCK_MODE", "true").lower() == "true"
        self.client = None
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "autolabmate-experiments")
        
        if not self.use_mock:
            self._initialize_pinecone()
        else:
            self._initialize_mock()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client"""
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY not set")
            
            pc = Pinecone(api_key=api_key)
            
            # Create or connect to index
            if self.index_name not in pc.list_indexes():
                pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI ada-002 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=os.getenv("PINECONE_CLOUD", "aws"),
                        region=os.getenv("PINECONE_REGION", "us-east-1")
                    )
                )
            
            self.client = pc.Index(self.index_name)
            logger.info("Pinecone initialized successfully")
            
        except Exception as e:
            logger.warning(f"Pinecone initialization failed: {str(e)}, using mock")
            self.use_mock = True
            self._initialize_mock()
    
    def _initialize_mock(self):
        """Initialize mock vector store"""
        self.mock_data = []
        logger.info("Vector store running in MOCK mode")
    
    async def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the vector store
        
        Args:
            text: Document text
            metadata: Optional metadata
            doc_id: Optional document ID
            
        Returns:
            Document ID
        """
        try:
            if self.use_mock:
                return await self._add_document_mock(text, metadata, doc_id)
            else:
                return await self._add_document_pinecone(text, metadata, doc_id)
                
        except Exception as e:
            logger.error(f"Add document error: {str(e)}")
            raise
    
    async def _add_document_mock(
        self,
        text: str,
        metadata: Optional[Dict],
        doc_id: Optional[str]
    ) -> str:
        """Mock implementation"""
        import uuid
        
        doc_id = doc_id or str(uuid.uuid4())
        self.mock_data.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {}
        })
        
        logger.info(f"Mock document added: {doc_id}")
        return doc_id
    
    async def _add_document_pinecone(
        self,
        text: str,
        metadata: Optional[Dict],
        doc_id: Optional[str]
    ) -> str:
        """Pinecone implementation"""
        # Generate embedding
        embedding = await self._get_embedding(text)
        
        # Upsert to Pinecone
        vector_metadata = {**(metadata or {}), "text": text}
        self.client.upsert([
            (doc_id, embedding, vector_metadata)
        ])
        
        logger.info(f"Pinecone document added: {doc_id}")
        return doc_id
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of similar documents
        """
        try:
            if self.use_mock:
                return await self._search_mock(query, top_k, filter_dict)
            else:
                return await self._search_pinecone(query, top_k, filter_dict)
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    async def _search_mock(
        self,
        query: str,
        top_k: int,
        filter_dict: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Mock search - returns recent documents"""
        results = []
        for doc in self.mock_data[-top_k:]:
            # Simple keyword matching for mock
            if any(keyword.lower() in doc["text"].lower() for keyword in query.split()):
                results.append({
                    "id": doc["id"],
                    "score": 0.8,  # Mock score
                    "metadata": doc["metadata"],
                    "text": doc["text"]
                })
        
        return results[:top_k]
    
    async def _search_pinecone(
        self,
        query: str,
        top_k: int,
        filter_dict: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Pinecone search implementation"""
        # Generate query embedding
        query_embedding = await self._get_embedding(query)
        
        # Query Pinecone
        results = self.client.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        formatted_results = []
        for match in results["matches"]:
            formatted_results.append({
                "id": match["id"],
                "score": match["score"],
                "metadata": match["metadata"],
                "text": match["metadata"].get("text", "")
            })
        
        return formatted_results
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            # Return mock embedding
            return [0.0] * 1536
    
    def is_available(self) -> bool:
        """Check if vector store is available"""
        return True  # Always available (mock or real)

