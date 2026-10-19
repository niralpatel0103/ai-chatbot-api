import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import text
from database import Chunk, is_postgres

# 384 dimensions for all-MiniLM-L6-v2
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks):
    """Generate embeddings for a list of text chunks"""
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings

def search_vectors(db, query_text, file_id, k=5):
    """
    Perform semantic search using pgvector directly in PostgreSQL,
    or in-memory cosine similarity fallback when running on SQLite.
    """
    # 1. Generate normalized embedding for the user's query
    query_vector = model.encode([query_text], normalize_embeddings=True)[0]

    # 2. Perform search based on database dialect
    if is_postgres:
        sql = text("""
            SELECT id, content, (embedding <=> :embedding) as distance
            FROM chunks
            WHERE file_id = :file_id
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """)

        results = db.execute(sql, {
            "embedding": str(query_vector.tolist()),
            "file_id": file_id,
            "limit": k
        }).fetchall()

        final_results = []
        for r in results:
            final_results.append({
                "id": r[0],
                "content": r[1],
                "similarity": 1 - float(r[2])  # Convert cosine distance to similarity
            })
        return final_results
    else:
        # SQLite fallback: calculate cosine similarity using normalized dot product
        chunks = db.query(Chunk).filter(Chunk.file_id == file_id).all()
        if not chunks:
            return []

        scored_chunks = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            try:
                emb = np.array(json.loads(chunk.embedding), dtype=np.float32)
                sim = float(np.dot(query_vector, emb))
                scored_chunks.append({
                    "id": chunk.id,
                    "content": chunk.content,
                    "similarity": sim
                })
            except Exception:
                continue

        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:k]