"""
Vector Store Core Module
Provides document embedding and semantic search functionality
Uses OpenAI for embeddings and in-memory storage for simplicity
Can be extended to use Qdrant for persistent storage
"""

import os
import json
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False


class VectorStore:
    """
    Vector store for document embeddings and semantic search.
    Supports both in-memory storage and Qdrant backend.
    """
    
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536
    
    def __init__(self, 
                 collection_name: str = "ds_star_knowledge",
                 use_qdrant: bool = False,
                 qdrant_url: Optional[str] = None,
                 persist_path: str = "vector_store_data"):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the vector collection
            use_qdrant: Whether to use Qdrant backend (requires running server)
            qdrant_url: URL for Qdrant server (default: in-memory)
            persist_path: Path for local persistence
        """
        self.collection_name = collection_name
        self.use_qdrant = use_qdrant and HAS_QDRANT
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        if HAS_OPENAI:
            api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        if self.use_qdrant:
            self._init_qdrant(qdrant_url)
        else:
            self._init_memory_store()
    
    def _init_qdrant(self, url: Optional[str]):
        """Initialize Qdrant client."""
        try:
            if url:
                self.qdrant = QdrantClient(url=url)
            else:
                self.qdrant = QdrantClient(":memory:")
            
            collections = self.qdrant.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not exists:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.EMBEDDING_DIM,
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Qdrant init error: {e}")
            self.use_qdrant = False
            self._init_memory_store()
    
    def _init_memory_store(self):
        """Initialize in-memory vector store."""
        self.memory_store = {
            "documents": [],
            "embeddings": [],
            "metadata": []
        }
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load persisted data from disk."""
        store_file = self.persist_path / f"{self.collection_name}.json"
        embeddings_file = self.persist_path / f"{self.collection_name}_embeddings.npy"
        
        if store_file.exists():
            try:
                with open(store_file, 'r') as f:
                    data = json.load(f)
                    self.memory_store["documents"] = data.get("documents", [])
                    self.memory_store["metadata"] = data.get("metadata", [])
                
                if embeddings_file.exists():
                    self.memory_store["embeddings"] = np.load(embeddings_file, allow_pickle=True).tolist()
            except Exception as e:
                print(f"Error loading vector store from disk: {e}")
    
    def _save_to_disk(self):
        """Persist data to disk."""
        store_file = self.persist_path / f"{self.collection_name}.json"
        embeddings_file = self.persist_path / f"{self.collection_name}_embeddings.npy"
        
        try:
            with open(store_file, 'w') as f:
                json.dump({
                    "documents": self.memory_store["documents"],
                    "metadata": self.memory_store["metadata"]
                }, f)
            
            if self.memory_store["embeddings"]:
                np.save(embeddings_file, np.array(self.memory_store["embeddings"]))
        except Exception as e:
            print(f"Error saving vector store to disk: {e}")
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for text using OpenAI."""
        if not self.client:
            return self._get_simple_embedding(text)
        
        try:
            response = self.client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return self._get_simple_embedding(text)
    
    def _get_simple_embedding(self, text: str) -> List[float]:
        """
        Simple fallback embedding using TF-IDF-like features.
        Creates deterministic embeddings based on word frequencies that
        produce meaningful cosine similarities for related content.
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        embedding = np.zeros(self.EMBEDDING_DIM)
        
        for i, word in enumerate(words):
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            indices = []
            for j in range(min(5, self.EMBEDDING_DIM)):
                idx = (word_hash + j * 31337) % self.EMBEDDING_DIM
                indices.append(idx)
            
            weight = 1.0 / (1 + np.log1p(i))
            for idx in indices:
                embedding[idx] += weight
        
        for char in text_lower:
            if char.isalpha():
                char_hash = int(hashlib.md5(char.encode()).hexdigest(), 16)
                idx = char_hash % self.EMBEDDING_DIM
                embedding[idx] += 0.1
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        else:
            np.random.seed(int(hashlib.md5(text.encode()).hexdigest()[:8], 16))
            embedding = np.random.randn(self.EMBEDDING_DIM)
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def add_document(self, 
                    content: str, 
                    metadata: Optional[Dict[str, Any]] = None,
                    doc_id: Optional[str] = None) -> str:
        """
        Add a document to the vector store.
        
        Args:
            content: Document text content
            metadata: Optional metadata dict
            doc_id: Optional document ID (auto-generated if not provided)
        
        Returns:
            Document ID
        """
        if not doc_id:
            doc_id = hashlib.md5(content.encode()).hexdigest()[:12]
        
        embedding = self._get_embedding(content)
        if embedding is None:
            raise ValueError("Failed to generate embedding")
        
        meta = metadata or {}
        meta["doc_id"] = doc_id
        meta["created_at"] = datetime.utcnow().isoformat()
        meta["content_preview"] = content[:200] + "..." if len(content) > 200 else content
        
        if self.use_qdrant:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=hash(doc_id) % (2**63),
                        vector=embedding,
                        payload={"content": content, **meta}
                    )
                ]
            )
        else:
            existing_idx = None
            for i, m in enumerate(self.memory_store["metadata"]):
                if m.get("doc_id") == doc_id:
                    existing_idx = i
                    break
            
            if existing_idx is not None:
                self.memory_store["documents"][existing_idx] = content
                self.memory_store["embeddings"][existing_idx] = embedding
                self.memory_store["metadata"][existing_idx] = meta
            else:
                self.memory_store["documents"].append(content)
                self.memory_store["embeddings"].append(embedding)
                self.memory_store["metadata"].append(meta)
            
            self._save_to_disk()
        
        return doc_id
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple documents to the vector store.
        
        Args:
            documents: List of dicts with 'content' and optional 'metadata', 'id'
        
        Returns:
            List of document IDs
        """
        doc_ids = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            doc_id = doc.get("id")
            
            if content:
                result_id = self.add_document(content, metadata, doc_id)
                doc_ids.append(result_id)
        
        return doc_ids
    
    def search(self, 
              query: str, 
              top_k: int = 5,
              min_score: float = 0.0,
              filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            min_score: Minimum similarity score threshold
            filter_metadata: Optional metadata filter
        
        Returns:
            List of matching documents with scores
        """
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return []
        
        if self.use_qdrant:
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            return [
                {
                    "content": r.payload.get("content", ""),
                    "metadata": {k: v for k, v in r.payload.items() if k != "content"},
                    "score": r.score
                }
                for r in results
                if r.score >= min_score
            ]
        else:
            if not self.memory_store["embeddings"]:
                return []
            
            similarities = []
            for i, emb in enumerate(self.memory_store["embeddings"]):
                score = self._cosine_similarity(query_embedding, emb)
                
                if score >= min_score:
                    meta = self.memory_store["metadata"][i]
                    
                    if filter_metadata:
                        match = all(
                            meta.get(k) == v for k, v in filter_metadata.items()
                        )
                        if not match:
                            continue
                    
                    similarities.append({
                        "content": self.memory_store["documents"][i],
                        "metadata": meta,
                        "score": score
                    })
            
            similarities.sort(key=lambda x: x["score"], reverse=True)
            return similarities[:top_k]
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if self.use_qdrant:
            try:
                self.qdrant.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=[hash(doc_id) % (2**63)]
                    )
                )
                return True
            except:
                return False
        else:
            for i, meta in enumerate(self.memory_store["metadata"]):
                if meta.get("doc_id") == doc_id:
                    self.memory_store["documents"].pop(i)
                    self.memory_store["embeddings"].pop(i)
                    self.memory_store["metadata"].pop(i)
                    self._save_to_disk()
                    return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        if self.use_qdrant:
            try:
                info = self.qdrant.get_collection(self.collection_name)
                return {
                    "backend": "qdrant",
                    "collection": self.collection_name,
                    "document_count": info.points_count,
                    "vector_size": info.config.params.vectors.size
                }
            except:
                pass
        
        return {
            "backend": "memory",
            "collection": self.collection_name,
            "document_count": len(self.memory_store["documents"]),
            "vector_size": self.EMBEDDING_DIM,
            "persist_path": str(self.persist_path)
        }
    
    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all documents in the store."""
        if self.use_qdrant:
            try:
                results = self.qdrant.scroll(
                    collection_name=self.collection_name,
                    limit=limit
                )
                return [
                    {
                        "doc_id": r.payload.get("doc_id"),
                        "content_preview": r.payload.get("content_preview", ""),
                        "metadata": {k: v for k, v in r.payload.items() 
                                   if k not in ["content", "doc_id", "content_preview"]}
                    }
                    for r in results[0]
                ]
            except:
                return []
        else:
            return [
                {
                    "doc_id": meta.get("doc_id"),
                    "content_preview": meta.get("content_preview", ""),
                    "metadata": {k: v for k, v in meta.items() 
                               if k not in ["doc_id", "content_preview"]}
                }
                for meta in self.memory_store["metadata"][:limit]
            ]
    
    def clear(self):
        """Clear all documents from the store."""
        if self.use_qdrant:
            try:
                self.qdrant.delete_collection(self.collection_name)
                self._init_qdrant(None)
            except:
                pass
        else:
            self.memory_store = {
                "documents": [],
                "embeddings": [],
                "metadata": []
            }
            store_file = self.persist_path / f"{self.collection_name}.json"
            embeddings_file = self.persist_path / f"{self.collection_name}_embeddings.npy"
            if store_file.exists():
                store_file.unlink()
            if embeddings_file.exists():
                embeddings_file.unlink()
