"""
Vector Database and RAG Infrastructure
Provides vector storage, retrieval, and RAG capabilities using ChromaDB
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import uuid
import hashlib

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from pydantic import BaseModel, Field

from app.core.ai_client import get_ai_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class Document(BaseModel):
    """Document model for vector storage."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Document embedding")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class QueryResult(BaseModel):
    """Query result model."""
    document: Document
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    rank: int = Field(..., description="Result rank")


class RAGResponse(BaseModel):
    """RAG response model."""
    answer: str = Field(..., description="Generated answer")
    sources: List[Document] = Field(..., description="Source documents")
    confidence: float = Field(..., description="Confidence score (0-1)")
    query: str = Field(..., description="Original query")
    model_used: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Tokens used")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        protected_namespaces = ()


class VectorDatabase:
    """Vector database manager using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collections: Dict[str, Collection] = {}
        self.logger = get_logger(__name__)
        
        # Collection configurations
        self.collection_configs = {
            "projects": {
                "description": "Project documents and metadata",
                "metadata_fields": ["project_id", "name", "status", "priority", "type"]
            },
            "features": {
                "description": "Feature specifications and documentation",
                "metadata_fields": ["feature_id", "name", "project_id", "status", "complexity"]
            },
            "backlogs": {
                "description": "Backlog items and user stories",
                "metadata_fields": ["backlog_id", "name", "priority", "status", "complexity"]
            },
            "resources": {
                "description": "Resource profiles and skills",
                "metadata_fields": ["resource_id", "name", "role", "skills", "experience"]
            },
            "documentation": {
                "description": "Technical documentation and guides",
                "metadata_fields": ["doc_type", "title", "version", "category"]
            },
            "code": {
                "description": "Code snippets and examples",
                "metadata_fields": ["file_path", "language", "function", "class"]
            },
            "meetings": {
                "description": "Meeting notes and decisions",
                "metadata_fields": ["meeting_id", "date", "participants", "type"]
            },
            "knowledge_base": {
                "description": "General knowledge base articles",
                "metadata_fields": ["category", "tags", "author", "version"]
            }
        }
    
    async def initialize(self):
        """Initialize the vector database."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create collections
            await self._create_collections()
            
            self.logger.info("Vector database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
            return False
    
    async def _create_collections(self):
        """Create all required collections."""
        for collection_name, config in self.collection_configs.items():
            try:
                # Check if collection exists
                try:
                    collection = self.client.get_collection(collection_name)
                    self.logger.info(f"Collection '{collection_name}' already exists")
                except:
                    # Create new collection
                    collection = self.client.create_collection(
                        name=collection_name,
                        metadata={"description": config["description"]}
                    )
                    self.logger.info(f"Created collection '{collection_name}'")
                
                self.collections[collection_name] = collection
                
            except Exception as e:
                self.logger.error(f"Failed to create collection '{collection_name}': {e}")
    
    async def add_document(
        self,
        collection_name: str,
        document: Document,
        generate_embedding: bool = True
    ) -> bool:
        """Add a document to the vector database."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Generate embedding if not provided
            if generate_embedding and not document.embedding:
                ai_service = await get_ai_service()
                document.embedding = await ai_service.ollama_client.generate_embeddings(
                    document.content
                )
            
            # Prepare metadata
            metadata = {
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
                **document.metadata
            }
            
            # Add document to collection
            collection.add(
                documents=[document.content],
                metadatas=[metadata],
                embeddings=[document.embedding] if document.embedding else None,
                ids=[document.id]
            )
            
            self.logger.info(f"Added document {document.id} to collection '{collection_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document to '{collection_name}': {e}")
            return False
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[Document],
        generate_embeddings: bool = True
    ) -> int:
        """Add multiple documents to the vector database."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Prepare data
            doc_contents = []
            doc_metadatas = []
            doc_embeddings = []
            doc_ids = []
            
            for document in documents:
                # Generate embedding if not provided
                if generate_embeddings and not document.embedding:
                    ai_service = await get_ai_service()
                    document.embedding = await ai_service.ollama_client.generate_embeddings(
                        document.content
                    )
                
                doc_contents.append(document.content)
                doc_metadatas.append({
                    "created_at": document.created_at.isoformat(),
                    "updated_at": document.updated_at.isoformat(),
                    **document.metadata
                })
                doc_embeddings.append(document.embedding)
                doc_ids.append(document.id)
            
            # Add documents to collection
            collection.add(
                documents=doc_contents,
                metadatas=doc_metadatas,
                embeddings=doc_embeddings,
                ids=doc_ids
            )
            
            self.logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return len(documents)
            
        except Exception as e:
            self.logger.error(f"Failed to add documents to '{collection_name}': {e}")
            return 0
    
    async def search_documents(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """Search for similar documents."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Generate query embedding
            ai_service = await get_ai_service()
            query_embedding = await ai_service.ollama_client.generate_embeddings(query)
            
            # Search for similar documents
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Convert results to QueryResult objects
            query_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc_content, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1 - distance
                    
                    document = Document(
                        id=results["ids"][0][i],
                        content=doc_content,
                        metadata=metadata,
                        created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
                    )
                    
                    query_result = QueryResult(
                        document=document,
                        similarity_score=similarity_score,
                        rank=i + 1
                    )
                    
                    query_results.append(query_result)
            
            self.logger.info(f"Found {len(query_results)} results for query in '{collection_name}'")
            return query_results
            
        except Exception as e:
            self.logger.error(f"Failed to search documents in '{collection_name}': {e}")
            return []
    
    async def get_document(self, collection_name: str, document_id: str) -> Optional[Document]:
        """Get a specific document by ID."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Get document
            results = collection.get(ids=[document_id])
            
            if results["documents"] and results["documents"][0]:
                metadata = results["metadatas"][0][0]
                return Document(
                    id=document_id,
                    content=results["documents"][0][0],
                    metadata=metadata,
                    created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id} from '{collection_name}': {e}")
            return None
    
    async def update_document(
        self,
        collection_name: str,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        regenerate_embedding: bool = True
    ) -> bool:
        """Update a document in the vector database."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Get existing document
            existing_doc = await self.get_document(collection_name, document_id)
            if not existing_doc:
                return False
            
            # Prepare update data
            update_data = {}
            if content is not None:
                update_data["documents"] = [content]
                existing_doc.content = content
            
            if metadata is not None:
                update_data["metadatas"] = [{
                    "created_at": existing_doc.created_at.isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    **metadata
                }]
                existing_doc.metadata.update(metadata)
            
            # Regenerate embedding if content changed
            if regenerate_embedding and content is not None:
                ai_service = await get_ai_service()
                embedding = await ai_service.ollama_client.generate_embeddings(content)
                update_data["embeddings"] = [embedding]
            
            # Update document
            collection.update(
                ids=[document_id],
                **update_data
            )
            
            self.logger.info(f"Updated document {document_id} in collection '{collection_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update document {document_id} in '{collection_name}': {e}")
            return False
    
    async def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from the vector database."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Delete document
            collection.delete(ids=[document_id])
            
            self.logger.info(f"Deleted document {document_id} from collection '{collection_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id} from '{collection_name}': {e}")
            return False
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Get collection info
            count = collection.count()
            
            return {
                "collection_name": collection_name,
                "document_count": count,
                "description": self.collection_configs[collection_name]["description"],
                "metadata_fields": self.collection_configs[collection_name]["metadata_fields"],
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats for collection '{collection_name}': {e}")
            return {}
    
    async def get_all_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections."""
        try:
            stats = {}
            total_documents = 0
            
            for collection_name in self.collections.keys():
                collection_stats = await self.get_collection_stats(collection_name)
                stats[collection_name] = collection_stats
                total_documents += collection_stats.get("document_count", 0)
            
            return {
                "collections": stats,
                "total_documents": total_documents,
                "total_collections": len(self.collections),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get all collection stats: {e}")
            return {}
    
    async def clear_collection(self, collection_name: str) -> bool:
        """Clear all documents from a collection."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            collection = self.collections[collection_name]
            
            # Delete all documents
            collection.delete()
            
            self.logger.info(f"Cleared collection '{collection_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear collection '{collection_name}': {e}")
            return False
    
    async def reset_database(self) -> bool:
        """Reset the entire vector database."""
        try:
            # Clear all collections
            for collection_name in self.collections.keys():
                await self.clear_collection(collection_name)
            
            self.logger.info("Reset vector database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset vector database: {e}")
            return False


class RAGService:
    """Retrieval-Augmented Generation service."""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.logger = get_logger(__name__)
    
    async def generate_answer(
        self,
        query: str,
        collection_names: Optional[List[str]] = None,
        top_k: int = 5,
        model: str = "llama3:8b",
        temperature: float = 0.3,
        include_sources: bool = True
    ) -> RAGResponse:
        """Generate an answer using RAG."""
        start_time = datetime.now()
        
        try:
            # Default to all collections if none specified
            if collection_names is None:
                collection_names = list(self.vector_db.collections.keys())
            
            # Search for relevant documents
            all_results = []
            for collection_name in collection_names:
                results = await self.vector_db.search_documents(
                    collection_name=collection_name,
                    query=query,
                    top_k=top_k
                )
                all_results.extend(results)
            
            # Sort by similarity score and take top results
            all_results.sort(key=lambda x: x.similarity_score, reverse=True)
            top_results = all_results[:top_k]
            
            if not top_results:
                return RAGResponse(
                    answer="I couldn't find relevant information to answer your question.",
                    sources=[],
                    confidence=0.0,
                    query=query,
                    model_used=model,
                    tokens_used=0,
                    response_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.now()
                )
            
            # Prepare context from retrieved documents
            context = self._prepare_context(top_results)
            
            # Generate answer using AI
            ai_service = await get_ai_service()
            
            messages = [
                AIMessage(
                    role="system",
                    content=f"""You are a helpful assistant that answers questions based on the provided context.
                    Use only the information from the context to answer the question.
                    If the context doesn't contain enough information to answer the question, say so.
                    Be accurate and cite specific information from the context when possible.
                    
                    Context:
                    {context}"""
                ),
                AIMessage(role="user", content=query)
            ]
            
            response = await ai_service.ollama_client.generate_text(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            # Calculate confidence based on similarity scores
            confidence = sum(result.similarity_score for result in top_results) / len(top_results)
            
            return RAGResponse(
                answer=response.content,
                sources=[result.document for result in top_results] if include_sources else [],
                confidence=confidence,
                query=query,
                model_used=model,
                tokens_used=response.tokens_used,
                response_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate RAG answer: {e}")
            return RAGResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence=0.0,
                query=query,
                model_used=model,
                tokens_used=0,
                response_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
    
    def _prepare_context(self, results: List[QueryResult]) -> str:
        """Prepare context from search results."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"Source {i} (Similarity: {result.similarity_score:.3f}):\n"
                f"{result.document.content}\n"
                f"Metadata: {result.document.metadata}\n"
            )
        
        return "\n".join(context_parts)
    
    async def generate_summary(
        self,
        collection_name: str,
        filter_metadata: Optional[Dict[str, Any]] = None,
        model: str = "llama3:8b",
        max_documents: int = 20
    ) -> RAGResponse:
        """Generate a summary of documents in a collection."""
        try:
            # Get documents from collection
            collection = self.vector_db.collections[collection_name]
            results = collection.get(
                limit=max_documents,
                where=filter_metadata
            )
            
            if not results["documents"] or not results["documents"][0]:
                return RAGResponse(
                    answer="No documents found to summarize.",
                    sources=[],
                    confidence=0.0,
                    query=f"Summary of {collection_name}",
                    model_used=model,
                    tokens_used=0,
                    response_time=0.0,
                    timestamp=datetime.now()
                )
            
            # Prepare context
            documents = []
            for i, (content, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
                doc = Document(
                    id=results["ids"][0][i],
                    content=content,
                    metadata=metadata
                )
                documents.append(doc)
            
            context = "\n\n".join([f"Document {i+1}:\n{doc.content}" for i, doc in enumerate(documents)])
            
            # Generate summary
            ai_service = await get_ai_service()
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a helpful assistant that creates comprehensive summaries.
                    Analyze the provided documents and create a well-structured summary that covers:
                    1. Key themes and topics
                    2. Important information and insights
                    3. Patterns and trends
                    4. Recommendations or conclusions
                    
                    Make the summary clear, organized, and informative."""
                ),
                AIMessage(
                    role="user",
                    content=f"Please create a comprehensive summary of the following documents from {collection_name}:\n\n{context}"
                )
            ]
            
            response = await ai_service.ollama_client.generate_text(
                model=model,
                messages=messages,
                temperature=0.4
            )
            
            return RAGResponse(
                answer=response.content,
                sources=documents,
                confidence=0.8,  # High confidence for summaries
                query=f"Summary of {collection_name}",
                model_used=model,
                tokens_used=response.tokens_used,
                response_time=0.0,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary for {collection_name}: {e}")
            return RAGResponse(
                answer=f"I encountered an error while generating the summary: {str(e)}",
                sources=[],
                confidence=0.0,
                query=f"Summary of {collection_name}",
                model_used=model,
                tokens_used=0,
                response_time=0.0,
                timestamp=datetime.now()
            )


# Global instances
vector_db: Optional[VectorDatabase] = None
rag_service: Optional[RAGService] = None


async def get_vector_db() -> VectorDatabase:
    """Get global vector database instance."""
    global vector_db
    if vector_db is None:
        vector_db = VectorDatabase()
        await vector_db.initialize()
    return vector_db


async def get_rag_service() -> RAGService:
    """Get global RAG service instance."""
    global rag_service
    if rag_service is None:
        vector_db_instance = await get_vector_db()
        rag_service = RAGService(vector_db_instance)
    return rag_service


async def initialize_vector_db() -> VectorDatabase:
    """Initialize vector database."""
    global vector_db
    vector_db = VectorDatabase()
    await vector_db.initialize()
    return vector_db
