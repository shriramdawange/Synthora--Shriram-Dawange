# src/utils/embeddings.py

import chromadb
from chromadb.config import Settings
import uuid
from pathlib import Path
import tempfile

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def chunk_text(text):
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append({"text": chunk, "index": idx})
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1
    return chunks


def build_vector_store(chunks, arxiv_id):
    """Build and store embeddings in Chroma"""
    
    # Create temp directory for Chroma
    temp_dir = Path(tempfile.gettempdir()) / f"chroma_{uuid.uuid4()}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Chroma client with persistent directory
    client = chromadb.PersistentClient(path=str(temp_dir))
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name=f"arxiv_{arxiv_id}",
        metadata={"arxiv_id": arxiv_id}
    )
    
    # Prepare data for insertion
    ids = []
    documents = []
    metadatas = []
    
    for idx, chunk in enumerate(chunks):
        ids.append(f"{arxiv_id}_chunk_{idx}")
        documents.append(chunk.get("text", ""))
        metadatas.append({
            "arxiv_id": arxiv_id,
            "section": chunk.get("section", "unknown"),
            "chunk_index": idx
        })
    
    # Add chunks to collection
    try:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Stored {len(chunks)} chunks in vector DB")
    except Exception as e:
        print(f"Error storing chunks: {e}")
    
    # Return path to persist directory
    return str(temp_dir)


def retrieve_chunks(vector_store_path, query, arxiv_id, top_k=3):
    """Retrieve relevant chunks from vector store"""
    
    try:
        # Reconnect to existing Chroma database
        client = chromadb.PersistentClient(path=vector_store_path)
        collection = client.get_collection(name=f"arxiv_{arxiv_id}")
        
        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        chunks = []
        if results["ids"] and len(results["ids"]) > 0:
            for idx, (chunk_id, doc, metadata) in enumerate(
                zip(results["ids"][0], results["documents"][0], results["metadatas"][0])
            ):
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": doc,
                    "section": metadata.get("section", "unknown"),
                    "similarity": results["distances"][0][idx] if "distances" in results else 0
                })
        
        return chunks
    
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return []