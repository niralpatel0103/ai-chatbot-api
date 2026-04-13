from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import text
from database import Chunk

# 384 dimensions for all-MiniLM-L6-v2
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks):
    """Generate embeddings for a list of text chunks"""
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings

def search_vectors(db, query_text, file_id, k=5):
    """
    Perform semantic search using pgvector directly in the database.
    This replaces the local FAISS index with a production-ready SQL query.
    """
    # 1. Generate the embedding for the user's query
    query_embedding = model.encode([query_text], normalize_embeddings=True)[0].tolist()
    
    # 2. Perform the semantic search filtered by the specific file_id
    # The <-> operator is L2 distance, result is sorted by similarity
    # We use a raw SQL query with pgvector support
    sql = text("""
        SELECT id, content, (embedding <=> :embedding) as distance
        FROM chunks
        WHERE file_id = :file_id
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)
    
    results = db.execute(sql, {
        "embedding": str(query_embedding),
        "file_id": file_id,
        "limit": k
    }).fetchall()
    
    # 3. Format results
    final_results = []
    for r in results:
        final_results.append({
            "id": r[0],
            "content": r[1],
            "similarity": 1 - float(r[2]) # Convert cosine distance to similarity
        })
        
    return final_results