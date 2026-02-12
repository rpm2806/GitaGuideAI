import os
import json
import logging
import asyncio
import numpy as np
from starlette.concurrency import run_in_threadpool
import httpx

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
        self.hf_token = os.getenv("HF_TOKEN")
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        
        if not self.hf_token:
            logger.warning("HF_TOKEN is not set. Inference API calls will be rate-limited or fail.")

    async def _get_embeddings(self, texts: list) -> np.ndarray:
        """Fetches embeddings from Hugging Face Inference API."""
        if not self.hf_token:
            raise ValueError("HF_TOKEN is required for Inference API.")

        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json={"inputs": texts, "options": {"wait_for_model": True}}
            )
            
            if response.status_code != 200:
                logger.error(f"HF Inference API Error: {response.text}")
                raise Exception(f"HF API Error: {response.status_code}")
                
            return np.array(response.json())

    async def ingest_data(self, json_path: str):
        """Loads data from JSON and fetches embeddings from HF Inference API."""
        if not os.path.exists(json_path):
            logger.warning(f"Data file not found at {json_path}. Skipping ingestion.")
            return
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Ingesting {len(data)} verses via HF Inference API...")
            
            self.documents = [f"{item['translation']} (Chapter {item['chapter']}, Verse {item['verse']})" for item in data]
            self.metadatas = [{
                "chapter": item['chapter'],
                "verse": item['verse'],
                "shloka": item.get('shloka', ''),
                "transliteration": item.get('transliteration', ''),
                "hindi_translation": item.get('hindi_translation', ''),
                "source": item.get('source_ref', 'unknown')
            } for item in data]
            
            # Batch process embeddings (HF API has limits on payload size)
            batch_size = 50
            all_embeddings = []
            
            for i in range(0, len(self.documents), batch_size):
                batch = self.documents[i:i + batch_size]
                logger.info(f"Fetching embeddings for batch {i//batch_size + 1}...")
                batch_embeddings = await self._get_embeddings(batch)
                all_embeddings.append(batch_embeddings)
                # Small sleep to be respectful of rate limits
                await asyncio.sleep(0.5)
            
            self.embeddings = np.vstack(all_embeddings)
            logger.info("Ingestion complete via HF Inference API.")
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")

    async def search(self, query: str, limit: int = 5):
        try:
            if self.embeddings is None or len(self.embeddings) == 0:
                return []

            # Get query embedding
            query_embedding = await self._get_embeddings([query])
            query_embedding = query_embedding[0] # Take the first and only result
            
            # Compute cosine similarity
            # Since vectors from this model are normalized, dot product is cosine similarity
            scores = np.dot(self.embeddings, query_embedding)
            
            # Get top-k indices
            top_k_indices = np.argsort(scores)[::-1][:limit]
            
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
