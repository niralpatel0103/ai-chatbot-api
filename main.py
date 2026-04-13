import os
import re
import json
import uuid
from datetime import timedelta
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from groq import Groq
from dotenv import load_dotenv

from database import engine, SessionLocal, Base, User, FileUpload, Chunk, ChatHistory, get_db, init_db
from utils.pdf_utils import extract_text_from_pdf
from utils.chunker import chunk_text
from utils.vector_store import create_embeddings, search_vectors
from utils.auth_utils import verify_password, get_password_hash, create_access_token, decode_access_token

# Load environment variables
load_dotenv()

# Initialize DB (creates tables and vector extension)
init_db()

app = FastAPI(title="NexusAI SaaS Backend")

# CORS
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200")
origins = [origin.strip() for origin in cors_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app", # Support Vercel previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Check your .env file")
client = Groq(api_key=api_key)

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ------------------ AUTH ENDPOINTS ------------------

@app.post("/auth/register")
def register(email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=email,
        password_hash=get_password_hash(password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------ MANAGEMENT ENDPOINTS ------------------

@app.post("/files/upload")
async def upload_pdf(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Temporary save for processing
    temp_path = f"data/temp_{uuid.uuid4().hex}_{file.filename}"
    os.makedirs("data", exist_ok=True)

    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 1. Extract text and chunks
        documents = extract_text_from_pdf(temp_path)
        if not documents:
            raise HTTPException(status_code=400, detail="No readable text in PDF")

        chunks_data = chunk_text(documents)

        # 2. Generate embeddings
        embeddings = create_embeddings(chunks_data)

        # 3. Save to DB
        new_file = FileUpload(
            user_id=current_user.id,
            filename=file.filename,
            api_key=uuid.uuid4().hex
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        # 4. Save chunks with vectors
        for i, (chunk, emb) in enumerate(zip(chunks_data, embeddings)):
            new_chunk = Chunk(
                file_id=new_file.id,
                user_id=current_user.id,
                content=chunk["content"],
                embedding=emb.tolist()
            )
            db.add(new_chunk)

        db.commit()

        return {
            "message": "File processed and stored",
            "file_id": new_file.id,
            "api_key": new_file.api_key,
            "chunks_count": len(chunks_data)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/files")
def list_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = db.query(FileUpload).filter(FileUpload.user_id == current_user.id).all()
    return [{"id": f.id, "filename": f.filename, "api_key": f.api_key, "created_at": f.created_at} for f in files]


@app.delete("/files/{file_id}")
def delete_file(file_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    file_record = db.query(FileUpload).filter(FileUpload.id == file_id, FileUpload.user_id == current_user.id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    db.delete(file_record)  # Cascades to chunks and history
    db.commit()
    return {"message": "File and all associated data deleted"}


# ------------------ CHAT ENDPOINTS (Public for widgets) ------------------

@app.get("/ask/{api_key}")
@app.post("/ask/{api_key}")
async def ask_via_api_key(api_key: str, q: str, db: Session = Depends(get_db)):
    # 1. Validate API Key
    file_record = db.query(FileUpload).filter(FileUpload.api_key == api_key).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Invalid API Key or file not found")

    # 2. Semantic Search in pgvector
    results = search_vectors(db, q, file_record.id, k=5)

    if not results:
        return {"answer": "I'm sorry, I couldn't find any relevant information in the provided documents."}

    context = "\n\n".join([r["content"] for r in results])

    # 3. Groq LLM Response
    prompt = f"""
    You are a helpful customer support assistant. 
    Use the following context to answer the user's question.
    If you don't know the answer, say you don't know. Do not make up info.

    Context:
    {context}

    Question: {q}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        answer = chat_completion.choices[0].message.content

        # 4. (Optional) Save to history
        new_history = ChatHistory(file_id=file_record.id, role="user", content=q)
        db.add(new_history)
        new_history_ai = ChatHistory(file_id=file_record.id, role="assistant", content=answer)
        db.add(new_history_ai)
        db.commit()

        return {
            "answer": answer,
            "sources": [{"content": r["content"][:100] + "..."} for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask/id/{user_id}/{file_id}")
async def ask_via_ids(user_id: int, file_id: int, q: str, db: Session = Depends(get_db)):
    # Backup route for internal dashboard use
    file_record = db.query(FileUpload).filter(FileUpload.id == file_id, FileUpload.user_id == user_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found for this user")

    return await ask_via_api_key(file_record.api_key, q, db)


@app.get("/")
def health_check():
    return {"status": "online", "service": "NexusAI Multi-Tenant Engine"}