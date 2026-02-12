import os
import json
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.model = None
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
        
        # Initialize components
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            # Use CPU for Render free tier compliance
            self.model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def ingest_data(self, json_path: str):
        """Loads data from JSON and computes embeddings in-memory."""
        if not os.path.exists(json_path):
            logger.warning(f"Data file not found at {json_path}. Skipping ingestion.")
            return
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Ingesting {len(data)} verses...")
            
            self.documents = [f"{item['translation']} (Chapter {item['chapter']}, Verse {item['verse']})" for item in data]
            self.metadatas = [{
                "chapter": item['chapter'],
                "verse": item['verse'],
                "shloka": item.get('shloka', ''),
                "transliteration": item.get('transliteration', ''),
                "hindi_translation": item.get('hindi_translation', ''),
                "source": item.get('source_ref', 'unknown')
            } for item in data]
            
            # Compute embeddings
            embeddings = self.model.encode(self.documents, normalize_embeddings=True)
            self.embeddings = np.array(embeddings)
            
            logger.info("Ingestion complete.")
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")

    async def search(self, query: str, limit: int = 5):
        try:
            if self.embeddings is None or len(self.embeddings) == 0:
                return []

            # Run blocking encoding in threadpool
            query_embedding = await run_in_threadpool(self.model.encode, query, normalize_embeddings=True)
            
            # Compute cosine similarity (dot product of normalized vectors)
            scores = np.dot(self.embeddings, query_embedding)
            
            # Get top-k indices
            top_k_indices = np.argsort(scores)[::-1][:limit]
            
            # Formatting results
            hits = []
            for idx in top_k_indices:
                hits.append({
                    "content": self.documents[idx],
                    "metadata": self.metadatas[idx]
                })
            return hits
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
