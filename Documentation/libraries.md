# Libraries Used - Detailed Guide

## 📚 Overview of All Libraries

---

## 🚀 FastAPI

### What is FastAPI?
FastAPI is a modern, fast web framework for building APIs with Python. It's like building a website but instead of showing web pages, it provides data that other programs can use.

### Why do we use it?
- **Super Fast**: One of the fastest Python frameworks available
- **Easy to Use**: Simple syntax that's easy to understand
- **Automatic Documentation**: Creates interactive API docs for free
- **Type Safety**: Catches errors before they happen

### Where is it used?
```python
# In main.py
from fastapi import FastAPI, UploadFile, File

app = FastAPI()  # Creates the web server

@app.post("/admin/upload")  # Creates an API endpoint
async def upload_pdf(file: UploadFile = File(...)):
    # Function to handle PDF uploads
```

### How does it work?
1. **Creates a web server** that listens for requests
2. **Defines endpoints** (URLs) that clients can call
3. **Handles requests** and returns JSON responses
4. **Validates data** automatically using Python types

---

## 📄 pdfplumber

### What is pdfplumber?
pdfplumber is a Python library that helps read PDF files and extract text, tables, and other content from them.

### Why do we use it?
- **Reliable**: Better than many PDF readers at handling complex PDFs
- **Preserves Layout**: Keeps the structure of the PDF intact
- **Page by Page**: Can read PDFs one page at a time

### Where is it used?
```python
# In utils/pdf_utils.py
import pdfplumber

def extract_text_from_pdf(file_path):
    documents = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                documents.append({
                    "page": page.number + 1,
                    "text": text
                })
    return documents
```

### How does it work?
1. **Opens the PDF file** using `pdfplumber.open()`
2. **Iterates through pages** one by one
3. **Extracts text** from each page
4. **Returns structured data** with page numbers and text

---

## 🧠 SentenceTransformer

### What is SentenceTransformer?
SentenceTransformer is an AI library that converts text into numbers (vectors) that represent the meaning of the text. This is called "embedding".

### Why do we use it?
- **Understands Meaning**: Knows that "cat" and "kitten" are similar
- **Fast Processing**: Can convert lots of text quickly
- **Pre-trained Models**: Uses AI models already trained on huge datasets

### Where is it used?
```python
# In utils/vector_store.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embeddings(chunks):
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings)
```

### How does it work?
1. **Loads a pre-trained AI model** (`all-MiniLM-L6-v2`)
2. **Takes text as input** (like "How do I reset my password?")
3. **Converts to numbers** (a 384-dimensional vector)
4. **Similar texts get similar numbers** (meaning is preserved)

---

## 🔍 FAISS

### What is FAISS?
FAISS (Facebook AI Similarity Search) is a library for efficiently searching and clustering vectors. It's like a super-fast search engine for numbers.

### Why do we use it?
- **Lightning Fast**: Can search millions of items in milliseconds
- **Memory Efficient**: Doesn't use much computer memory
- **Scalable**: Works with small or huge datasets

### Where is it used?
```python
# In utils/vector_store.py
import faiss

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]  # Size of each vector
    index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
    index.add(embeddings)  # Add all embeddings to the index
    return index

def search(query, index, chunks, k=3):
    query_embedding = model.encode([query], normalize_embeddings=True)
    distances, indices = index.search(np.array(query_embedding), k)
    # Returns the most similar chunks
```

### How does it work?
1. **Creates an index** (like a smart database)
2. **Adds all document embeddings** to the index
3. **When searching**, compares query embedding with all stored ones
4. **Returns the most similar** ones with similarity scores

---

## 🤖 Groq

### What is Groq?
Groq is a service that provides fast access to powerful AI language models (like Llama, Mixtral, etc.) for generating human-like text.

### Why do we use it?
- **Fast Responses**: Very quick API responses
- **Multiple Models**: Access to different AI models
- **Reliable**: Stable service with good uptime

### Where is it used?
```python
# In main.py
from groq import Groq

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)
answer = response.choices[0].message.content
```

### How does it work?
1. **Sends a prompt** to Groq's AI model
2. **AI model processes** the prompt and context
3. **Returns a response** that sounds human-like
4. **We clean the response** to make it customer-friendly

---

## 🔢 NumPy

### What is NumPy?
NumPy is a fundamental package for scientific computing in Python. It provides support for large, multi-dimensional arrays and matrices.

### Why do we use it?
- **Fast Math**: Very fast mathematical operations
- **Array Operations**: Easy to work with lists of numbers
- **Memory Efficient**: Better than Python lists for numerical data

### Where is it used?
```python
# In utils/vector_store.py
import numpy as np

# Convert embeddings to numpy array
embeddings = np.array(embeddings)

# Convert query to numpy array for search
query_embedding = np.array(query_embedding)
```

### How does it work?
1. **Creates arrays** from lists of numbers
2. **Performs math operations** quickly
3. **Handles multi-dimensional data** (like embedding vectors)

---

## 🔐 python-dotenv

### What is python-dotenv?
python-dotenv is a library that reads key-value pairs from a `.env` file and adds them to the environment variables.

### Why do we use it?
- **Security**: Keeps secrets (like API keys) out of code
- **Flexibility**: Different settings for different environments
- **Convenience**: Easy to manage configuration

### Where is it used?
```python
# In main.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file
api_key = os.getenv("GROQ_API_KEY")  # Get the API key
```

### How does it works?
1. **Looks for .env file** in the project directory
2. **Reads key-value pairs** like `GROQ_API_KEY=abc123`
3. **Makes them available** as environment variables
4. **We access them** using `os.getenv()`

---

## 🔍 re (Regular Expressions)

### What is re?
The `re` module is Python's built-in library for working with regular expressions - patterns for matching text.

### Why do we use it?
- **Pattern Matching**: Find specific text patterns
- **Text Extraction**: Pull out specific parts of text
- **Validation**: Check if text matches a format

### Where is it used?
```python
# In main.py
import re

# Find questions in text
pattern = r"(?i)(question\s*\d+[\s\:\.\-\)]+.*?)(?=question\s*\d+[\s\:\.\-\)]+|$)"
matches = re.findall(pattern, text, re.DOTALL)

# Find question numbers
q_num_match = re.search(r"question\s*(\d+)", q, re.IGNORECASE)
```

### How does it work?
1. **Defines patterns** using special syntax
2. **Searches text** for matching patterns
3. **Extracts matches** for further processing
4. **Handles variations** (like "Question 1:", "Q1", "question 1.")

---

## 📊 Summary of How Libraries Work Together

```
User uploads PDF → pdfplumber reads it → re finds questions → 
SentenceTransformer creates embeddings → FAISS stores them → 
User asks question → SentenceTransformer converts question → 
FAISS finds similar chunks → Groq generates answer → 
FastAPI returns clean response
```

Each library has a specific job, and together they create a complete AI customer support system!
