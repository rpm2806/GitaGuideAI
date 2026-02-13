
import asyncio
import os
import argparse
from rag import RAGPipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_index")

async def build_index(data_path: str, output_dir: str):
    """
    Builds the RAG index and saves it to the output directory.
    """
    if not os.path.exists(data_path):
        logger.error(f"Data file not found at {data_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rag = RAGPipeline()
    
    # Ingest data (this fetches embeddings)
    logger.info(f"Ingesting data from {data_path}...")
    await rag.ingest_data(data_path)
    
    # Save to cache
    logger.info(f"Saving index to {output_dir}...")
    rag.save_index(output_dir)
    logger.info("Index built and saved successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build RAG Index")
    parser.add_argument("--data", type=str, default="data/gita.json", help="Path to data JSON file")
    parser.add_argument("--output", type=str, default="data_cache", help="Directory to save index files")
    
    args = parser.parse_args()
    
    asyncio.run(build_index(args.data, args.output))
