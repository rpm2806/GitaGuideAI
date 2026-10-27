import os
import json
import logging
import asyncio
import numpy as np
from starlette.concurrency import run_in_threadpool
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
        self.hf_token = os.getenv("HF_TOKEN")
        if self.hf_token:
            self.hf_token = self.hf_token.strip()
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"

    def _build_tfidf(self):
        """Builds an in-memory TF-IDF index over the documents for instant, resilient retrieval."""
        if self.documents:
            try:
                self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
                self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
                logger.info(f"TF-IDF search index initialized for {len(self.documents)} verses.")
            except Exception as e:
                logger.error(f"Failed to build TF-IDF index: {e}")

    async def _get_embeddings(self, texts: list) -> np.ndarray:
        """Fetches embeddings from Hugging Face Inference API."""
        if not self.hf_token:
            raise ValueError("HF_TOKEN is required for Inference API.")

        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json={"inputs": texts, "options": {"wait_for_model": True}}
            )
            
            if response.status_code != 200:
                logger.warning(f"HF Inference API Error {response.status_code}: {response.text[:200]}")
                raise Exception(f"HF API Error: {response.status_code}")
                
            return np.array(response.json())

    async def ingest_data(self, json_path: str, index_path: str = "data_cache"):
        """Loads data from JSON and initializes retrieval indices."""
        # Check cache first
        if self.load_index(index_path):
            self._build_tfidf()
            return

        if not os.path.isabs(json_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            candidate = os.path.join(base_dir, json_path)
            if os.path.exists(candidate):
                json_path = candidate

        if not os.path.exists(json_path):
            logger.warning(f"Data file not found at {json_path}. Skipping ingestion.")
            return
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Ingesting {len(data)} verses...")
            
            self.documents = [f"{item.get('translation', '')} (Chapter {item['chapter']}, Verse {item['verse']})" for item in data]
            self.metadatas = [{
                "chapter": item['chapter'],
                "verse": item['verse'],
                "shloka": item.get('shloka', ''),
                "transliteration": item.get('transliteration', ''),
                "hindi_translation": item.get('hindi_translation', ''),
                "source": item.get('source_ref', 'unknown'),
                "text": item.get('translation', '')
            } for item in data]
            
            # Build fast TF-IDF index first
            self._build_tfidf()

            # Attempt HF Inference embeddings if token available
            if self.hf_token:
                try:
                    batch_size = 50
                    all_embeddings = []
                    for i in range(0, len(self.documents), batch_size):
                        batch = self.documents[i:i + batch_size]
                        batch_embeddings = await self._get_embeddings(batch)
                        all_embeddings.append(batch_embeddings)
                        await asyncio.sleep(0.3)
                    self.embeddings = np.vstack(all_embeddings)
                    self.save_index(index_path)
                    logger.info("Ingestion complete via HF Inference API.")
                except Exception as e:
                    logger.warning(f"Remote embeddings skipped, using local search: {e}")
            else:
                logger.info("Ingestion complete using local search index.")
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")

    def save_index(self, directory: str):
        """Saves embeddings, documents, and metadatas to disk."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        if self.embeddings is not None and getattr(self.embeddings, 'ndim', 0) == 2:
            np.save(os.path.join(directory, "embeddings.npy"), self.embeddings)
        with open(os.path.join(directory, "documents.json"), "w", encoding="utf-8") as f:
            json.dump(self.documents, f)
        with open(os.path.join(directory, "metadatas.json"), "w", encoding="utf-8") as f:
            json.dump(self.metadatas, f)
            
    def load_index(self, directory: str) -> bool:
        """Loads index from disk. Returns True if successful."""
        try:
            if not os.path.isabs(directory):
                base_dir = os.path.dirname(os.path.abspath(__file__))
                candidate = os.path.join(base_dir, directory)
                if os.path.exists(candidate):
                    directory = candidate

            doc_path = os.path.join(directory, "documents.json")
            meta_path = os.path.join(directory, "metadatas.json")
            emb_path = os.path.join(directory, "embeddings.npy")
            
            if not (os.path.exists(doc_path) and os.path.exists(meta_path)):
                return False
                
            with open(doc_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadatas = json.load(f)

            # Ensure 'text' field exists in each metadata
            for i, meta in enumerate(self.metadatas):
                if "text" not in meta or not meta["text"]:
                    if i < len(self.documents):
                        raw_doc = self.documents[i]
                        meta["text"] = raw_doc.rsplit(" (Chapter", 1)[0] if " (Chapter" in raw_doc else raw_doc
                
            if os.path.exists(emb_path):
                try:
                    loaded = np.load(emb_path, allow_pickle=True)
                    if hasattr(loaded, 'ndim') and loaded.ndim == 2:
                        self.embeddings = loaded
                    else:
                        self.embeddings = None
                except Exception:
                    self.embeddings = None
                    
            logger.info("Loaded index from cache.")
            return True
        except Exception as e:
            logger.error(f"Failed to load index from cache: {e}")
            return False

    async def search(self, query: str, limit: int = 3):
        """Searches for the most relevant verses using vector embeddings or TF-IDF."""
        hits = []
        
        # 1. Try vector embeddings if available and valid
        if self.embeddings is not None and getattr(self.embeddings, 'ndim', 0) == 2:
            try:
                query_embedding = await self._get_embeddings([query])
                query_embedding = query_embedding[0]
                scores = np.dot(self.embeddings, query_embedding)
                top_k_indices = np.argsort(scores)[::-1][:limit]
                for idx in top_k_indices:
                    hits.append({
                        "content": self.documents[idx],
                        "metadata": self.metadatas[idx]
                    })
                if hits:
                    return hits
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to local search: {e}")

        # 2. Resilient local search via TF-IDF
        if self.vectorizer is not None and self.tfidf_matrix is not None:
            try:
                q_vec = self.vectorizer.transform([query])
                scores = (self.tfidf_matrix * q_vec.T).toarray().flatten()
                top_k_indices = np.argsort(scores)[::-1][:limit]
                for idx in top_k_indices:
                    hits.append({
                        "content": self.documents[idx],
                        "metadata": self.metadatas[idx]
                    })
                return hits
            except Exception as e:
                logger.error(f"Local TF-IDF search failed: {e}")

        # 3. Fallback: return first few verses if available
        if self.documents:
            return [{"content": self.documents[i], "metadata": self.metadatas[i]} for i in range(min(limit, len(self.documents)))]
            
        return []
