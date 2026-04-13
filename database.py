import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv
from pgvector.sqlalchemy import Vector

load_dotenv()

# Will fall back to local SQLite if Supabase URL is not provided yet
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Ensure compatibility with SQLAlchemy's postgres dialect 
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Only use pgvector if we are connecting to a Postgres database
is_postgres = DATABASE_URL.startswith("postgresql")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    files = relationship("FileUpload", back_populates="owner", cascade="all, delete-orphan")


class FileUpload(Base):
    __tablename__ = "file_uploads"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    # api_key used for the /ask/apikey endpoint
    api_key = Column(String, unique=True, index=True, default=lambda: uuid.uuid4().hex, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="files")
    chunks = relationship("Chunk", back_populates="file", cascade="all, delete-orphan")
    history = relationship("ChatHistory", back_populates="file", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    # 384 dimensions for all-MiniLM-L6-v2
    embedding = Column(Vector(384)) if is_postgres else Column(Text) # Fallback for local sqlite testing
    
    file = relationship("FileUpload", back_populates="chunks")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    file = relationship("FileUpload", back_populates="history")


# function that auto-creates all tables in Supabase 
def init_db():
    if is_postgres:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    Base.metadata.create_all(bind=engine)

# Dependency generator for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
