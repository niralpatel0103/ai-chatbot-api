# Backend Installation & Library Guide

This guide provides a complete list of libraries used in the NexusAI backend, how to install them, and why they are essential for the system.

## 🚀 Quick Installation

To install all required libraries at once, run the following command in your terminal (inside your virtual environment):

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary bcrypt==3.2.2 passlib python-jose[cryptography] python-dotenv groq sentence-transformers pdfplumber
```

---

## 🛠️ Detailed Library Breakdown

### 🔐 Bcrypt (The Compatibility Fix)
**Installation**: `pip install bcrypt==3.2.2`

> [!IMPORTANT]
> **Why the specific version?** 
> We use version `3.2.2` because the newer `bcrypt 4.0+` is incompatible with the `passlib` library used for security. Using a newer version causes a "ValueError: password cannot be longer than 72 bytes" crash during registration. 
> 
> **Where is it used?**
> It is used indirectly by `passlib` inside `utils/auth_utils.py` to securely hash user passwords before saving them to Supabase.

---

### 🏛️ SQLAlchemy
**Installation**: `pip install sqlalchemy`

*   **What**: An Object-Relational Mapper (ORM).
*   **Why**: It allows us to interact with the Supabase database using Python classes instead of writing raw SQL queries.
*   **Where is it used?** 
    *   `database.py`: To define tables like `User`, `FileUpload`, and `ChatHistory`.
    *   `main.py`: To perform database operations (add user, query history).

---

### 🐘 Psycopg2-Binary
**Installation**: `pip install psycopg2-binary`

*   **What**: The PostgreSQL adapter for Python.
*   **Why**: This is the "driver" that allows SQLAlchemy to talk to the PostgreSQL database hosted on Supabase. Without this, the connection will fail.
*   **Where is it used?**
    *   Used internally by the `DATABASE_URL` connection string in `.env`.

---

### ⚡ FastAPI & Uvicorn
**Installation**: `pip install fastapi uvicorn`

*   **What**: FastAPI is the web framework; Uvicorn is the server that runs it.
*   **Why**: Provides the high-performance API structure and automatic documentation (Swagger).
*   **Where is it used?** 
    *   `main.py`: Defines all routes like `/auth/register`, `/auth/login`, and `/chat`.

---

### 🤖 Groq
**Installation**: `pip install groq`

*   **What**: The client for the Groq Cloud API.
*   **Why**: Connects to powerful Large Language Models (LLMs) to generate the chatbot's answers.
*   **Where is it used?**
    *   `main.py`: Inside the `@app.post("/chat")` endpoint to process user queries.

---

### 🧠 Sentence-Transformers
**Installation**: `pip install sentence-transformers`

*   **What**: An AI library for text embeddings.
*   **Why**: Converts text into mathematical vectors (numbers) so we can perform "semantic search" (finding answers by meaning rather than just keywords).
*   **Where is it used?**
    *   `utils/vector_store.py`: To generate and search through text vectors.

---

### 📄 PDFPlumber
**Installation**: `pip install pdfplumber`

*   **What**: A robust PDF text extraction library.
*   **Why**: Allows the admin to upload PDFs and have the system read and learn from the text inside them.
*   **Where is it used?**
    *   `utils/pdf_utils.py`: To extract text page-by- trucks from uploaded files.

---

### 📝 Python-Dotenv
**Installation**: `pip install python-dotenv`

*   **What**: A tool to load settings from a `.env` file.
*   **Why**: Keeps your sensitive data (Supabase URL, API Keys) out of the main code for security.
*   **Where is it used?**
    *   Loaded at the top of `main.py` and `database.py`.

---

## 🔄 Summary of Updates

| Library | Action | Reason |
| :--- | :--- | :--- |
| **Bcrypt** | Downgraded to 3.2.2 | Fixed the "72-byte" crash during registration. |
| **CORS Middleware** | Updated Origins | Explicitly allowed `localhost:4200` to fix browser blocking. |
| **DATABASE_URL** | Switched to Pooler | Used Port 6543 to support IPv4 connections for local development. |
