# AI Customer Support System - Complete Documentation

## 📚 Table of Contents
1. [What is this Project?](#what-is-this-project)
2. [How the System Works](#how-the-system-works)
3. [Libraries Used](#libraries-used)
4. [API Endpoints](#api-endpoints)
5. [Project Structure](#project-structure)
6. [How to Run the Project](#how-to-run-the-project)
7. [Frequently Asked Questions](#frequently-asked-questions)

---

## 🎯 What is this Project?

Imagine you have a big PDF file with lots of questions and answers (like a FAQ document). This project creates an AI assistant that can read that PDF and answer questions about it, just like a real customer support agent!

**Example:**
- You upload a PDF with 100 FAQ questions
- A user asks: "How do I reset my password?"
- The AI finds the answer in the PDF and responds: "You can reset your password by clicking 'Forgot Password' on the login page"

---

## 🔧 How the System Works

The system works like a smart librarian who has read all your documents and can answer questions about them:

### Step 1: Upload PDF
- Admin uploads a PDF file with questions and answers
- System reads the PDF and extracts all the text

### Step 2: Break into Chunks
- The PDF text is broken into small pieces (chunks)
- Each chunk contains some questions and answers

### Step 3: Create AI Brain (Embeddings)
- Each chunk is converted into numbers (called embeddings)
- These numbers help the AI understand what each chunk is about
- Think of it like giving each chunk a unique "fingerprint"

### Step 4: Store in Memory
- All chunks and their fingerprints are stored in a special database (FAISS)
- This makes searching super fast!

### Step 5: Answer Questions
- When a user asks a question, the AI:
  1. Converts the question into numbers (fingerprint)
  2. Finds the most similar chunks in the database
  3. Shows those chunks to a smart AI model (LLM)
  4. The AI model gives a clean, helpful answer

---

## 📚 Libraries Used

### 1. FastAPI
**What it is:** A super-fast web framework for building APIs
**Why we use it:** To create the web server that handles requests
**Where used:** `main.py` - creates all the API endpoints

### 2. pdfplumber
**What it is:** A tool for reading PDF files
**Why we use it:** To extract text from uploaded PDFs
**Where used:** `utils/pdf_utils.py` - reads PDF page by page

### 3. SentenceTransformer
**What it is:** An AI tool that converts text into numbers (embeddings)
**Why we use it:** To create "fingerprints" of text chunks for smart searching
**Where used:** `utils/vector_store.py` - converts text to embeddings

### 4. FAISS
**What it is:** Facebook's super-fast library for searching similar items
**Why we use it:** To find the most relevant text chunks quickly
**Where used:** `utils/vector_store.py` - stores and searches embeddings

### 5. Groq
**What it is:** A service that provides access to powerful AI models (LLM)
**Why we use it:** To generate human-like answers from the found text
**Where used:** `main.py` - calls the AI model to create responses

### 6. sentence-transformers
**What it is:** The same as SentenceTransformer (just the package name)
**Why we use it:** For creating text embeddings
**Where used:** `utils/vector_store.py`

### 7. numpy
**What it is:** A library for working with numbers and arrays
**Why we use it:** To handle the embedding numbers efficiently
**Where used:** `utils/vector_store.py` - processes embedding arrays

### 8. python-dotenv
**What it is:** A tool to manage environment variables
**Why we use it:** To safely store the API key
**Where used:** `main.py` - loads the GROQ_API_KEY

### 9. re (Regular Expressions)
**What it is:** Python's built-in tool for pattern matching
**Why we use it:** To find questions in the text (like "Question 1:", "Question 2:")
**Where used:** `main.py` - extracts questions from text

---

## 🌐 API Endpoints

### Admin Endpoints (Only for uploading PDFs)

#### POST `/admin/upload`
**What it does:** Uploads and processes a PDF file
**How it works:**
1. Receives PDF file from frontend
2. Uses `pdfplumber` to extract text
3. Uses regex to find all questions
4. Uses `SentenceTransformer` to create embeddings
5. Uses `FAISS` to store embeddings
6. Saves everything to files

**Libraries used:**
- `pdfplumber` - read PDF
- `re` - find questions
- `SentenceTransformer` - create embeddings
- `FAISS` - store embeddings
- `DataManager` - save to files

#### GET `/admin/status`
**What it does:** Shows system status
**How it works:** Checks if PDF data exists and shows uploaded files

#### GET `/admin/questions`
**What it does:** Shows all extracted questions
**How it works:** Loads questions from storage and analyzes topics

#### GET `/admin/clear-chat`
**What it does:** Clears chat history
**How it works:** Deletes the chat history file

### Client Endpoint (For asking questions)

#### GET `/ask?q=your_question`
**What it does:** Answers user questions
**How it works:**
1. Understands what the user wants (intent)
2. Searches for relevant chunks using `FAISS`
3. Shows chunks to AI model using `Groq`
4. Cleans the response to be customer-friendly
5. Returns clean answer

**Libraries used:**
- `SentenceTransformer` - convert question to embedding
- `FAISS` - find similar chunks
- `Groq` - generate answer
- Response cleaner - remove unwanted text

---

## 📁 Project Structure

```
ai-chatbot/
├── main.py                 # Main server file with API endpoints
├── main_fixed.py          # Fixed version (production ready)
├── frontend.html          # Simple web interface
├── .env                   # Contains API key (hidden)
├── requirements.txt        # List of all libraries needed
├── utils/                 # Helper functions
│   ├── pdf_utils.py       # PDF reading functions
│   ├── chunker.py         # Text chunking functions
│   ├── vector_store.py    # Embedding and search functions
│   ├── data_manager.py    # File storage functions
│   └── qa_extractor.py    # Question-answer extraction
├── data/                  # Storage folder
│   ├── questions_store.json
│   ├── sections_store.json
│   ├── current_chunks.json
│   ├── faiss_index.bin
│   ├── chat_history.json
│   └── uploaded_pdfs/
└── Documentation/         # This folder
    ├── README.md         # Main documentation
    ├── libraries.md      # Detailed library info
    └── api_guide.md      # API usage guide
```

---

## 🚀 How to Run the Project

### Step 1: Install Libraries
```bash
pip install fastapi uvicorn pdfplumber sentence-transformers faiss-cpu groq python-dotenv
```

### Step 2: Set Up API Key
Create a `.env` file with:
```
GROQ_API_KEY=your_api_key_here
```

### Step 3: Start the Server
```bash
uvicorn main_fixed:app --reload
```

### Step 4: Use the Frontend
Open `frontend.html` in your browser or use the API directly.

---

## ❓ Frequently Asked Questions

### Q: Why do we need embeddings?
A: Imagine you have 1000 questions. Searching through all of them would be slow. Embeddings are like giving each question a unique "fingerprint" so the computer can find similar ones instantly!

### Q: What's the difference between FAISS and a normal database?
A: FAISS is specially designed for finding similar items quickly. A normal database is good for exact matches, but FAISS is great for finding "close enough" matches.

### Q: Why do we clean the AI response?
A: Sometimes the AI says things like "Based on the context..." which sounds robotic. We clean it to sound like a helpful human support agent.

### Q: Can this work with any PDF?
A: Yes! As long as the PDF has questions and answers in a clear format (like "Question 1: Answer..."), the system can handle any topic - medical, technical, educational, etc.

### Q: Is this safe for customer data?
A: All data is stored locally in the `data/` folder. You control where it goes and who has access.

---

## 🎉 Summary

This project creates a smart customer support system that:
1. **Reads** PDF documents with FAQs
2. **Understands** what users are asking
3. **Finds** relevant information quickly
4. **Responds** with helpful, human-like answers

It's like having a 24/7 customer support agent who knows all your documentation perfectly!
