# API Guide - Complete Reference

## 🌐 API Endpoints Overview

This system has two types of endpoints:
- **Admin Endpoints**: For uploading and managing PDFs
- **Client Endpoint**: For asking questions

---

## 🔧 Admin Endpoints

### POST `/admin/upload`

**Purpose**: Upload and process a PDF file

**How to use**:
```bash
curl -X POST "http://localhost:8000/admin/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

**What happens inside**:
1. **File Validation**: Checks if it's a PDF
2. **Text Extraction**: Uses `pdfplumber` to read the PDF
3. **Question Finding**: Uses `re` (regex) to find all questions
4. **Text Chunking**: Breaks text into manageable pieces
5. **Embedding Creation**: Uses `SentenceTransformer` to create vectors
6. **Index Building**: Uses `FAISS` to create searchable index
7. **File Storage**: Saves everything using `DataManager`

**Libraries used**:
- `pdfplumber` - Extract text from PDF
- `re` - Find question patterns
- `SentenceTransformer` - Create embeddings
- `FAISS` - Build search index
- `DataManager` - Save to files

**Response**:
```json
{
  "message": "PDF processed and stored successfully",
  "total_chunks": 45,
  "total_questions_extracted": 30,
  "document_topics": ["account", "payment", "technical"],
  "chunks_saved_at": "data/your_document.pdf_chunks.json",
  "ready_for_clients": true
}
```

---

### GET `/admin/status`

**Purpose**: Check system status

**How to use**:
```bash
curl "http://localhost:8000/admin/status"
```

**What happens inside**:
1. **Data Check**: Verifies if PDF data exists
2. **File List**: Gets list of uploaded PDFs
3. **Chat Check**: Checks chat history length

**Libraries used**:
- `DataManager` - Check stored data

**Response**:
```json
{
  "data_exists": true,
  "uploaded_files": ["faq.pdf", "manual.pdf"],
  "chat_history_length": 15
}
```

---

### GET `/admin/questions`

**Purpose**: View all extracted questions

**How to use**:
```bash
curl "http://localhost:8000/admin/questions"
```

**What happens inside**:
1. **Load Questions**: Gets questions from storage
2. **Topic Analysis**: Analyzes what topics are covered
3. **Format Response**: Returns structured data

**Libraries used**:
- `DataManager` - Load stored questions
- `analyze_document_topics()` - Detect topics

**Response**:
```json
{
  "total_questions": 30,
  "document_topics": ["account", "payment", "technical"],
  "questions": {
    "Q1": {
      "question_num": 1,
      "content": "Question 1: How do I reset my password? Answer: Click 'Forgot Password'..."
    },
    "Q2": {
      "question_num": 2,
      "content": "Question 2: How do I update my email? Answer: Go to account settings..."
    }
  }
}
```

---

### GET `/admin/clear-chat`

**Purpose**: Clear chat history

**How to use**:
```bash
curl "http://localhost:8000/admin/clear-chat"
```

**What happens inside**:
1. **Delete History**: Removes chat history file
2. **Return Confirmation**: Confirms operation

**Libraries used**:
- `DataManager` - Clear chat history

**Response**:
```json
{
  "message": "Chat history cleared by admin"
}
```

---

## 🤖 Client Endpoint

### GET `/ask?q=your_question`

**Purpose**: Ask questions and get answers

**How to use**:
```bash
curl "http://localhost:8000/ask?q=how%20do%20I%20reset%20my%20password"
```

**What happens inside**:

#### Step 1: Intent Understanding
```python
intent = understand_user_query(q)
```
- **Analyzes the question** to understand what user wants
- **Classifies as "faq" or "counting"**
- **Detects specific question numbers** if mentioned

**Libraries used**: `re` (regex) for pattern matching

#### Step 2: Direct Question Lookup (if applicable)
```python
if intent["type"] == "faq" and intent.get("question_number"):
    # Direct lookup for "question 5"
```
- **Checks if user asked for a specific question**
- **Returns the exact answer** if found

#### Step 3: Counting Queries
```python
if intent["type"] == "counting":
    # Handle "how many" questions
```
- **Uses all questions as context**
- **Calls Groq AI model** to count and analyze
- **Returns count with details**

**Libraries used**: `Groq` for AI analysis

#### Step 4: Semantic Search
```python
results = search(q, index_store, chunks_store, k=3)
```
- **Converts question to embedding** using `SentenceTransformer`
- **Searches FAISS index** for similar chunks
- **Gets top 3 most relevant chunks**

**Libraries used**: `SentenceTransformer`, `FAISS`

#### Step 5: AI Response Generation
```python
prompt = """You are a customer support assistant.
Answer user's question using provided context.
Rules:
Give a direct answer only
Do NOT explain reasoning
Do NOT mention context
Do NOT mention question numbers
Keep the answer short and clear
If answer is not found, say: 'Sorry, I couldn't find that information.'

Context: {context}
User Query: {q}"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)
```

- **Creates a customer-support prompt**
- **Sends context and question to Groq**
- **Gets AI-generated response**

**Libraries used**: `Groq` for AI generation

#### Step 6: Response Cleaning
```python
answer = clean_response(response.choices[0].message.content.strip())
```
- **Removes unwanted phrases** like "Based on context..."
- **Cleans up formatting**
- **Ensures customer-friendly response**

**Libraries used**: `re` (regex) for text cleaning

**Response**:
```json
{
  "answer": "You can reset your password by clicking 'Forgot Password' on the login page.",
  "intent": {
    "type": "faq"
  }
}
```

---

## 🔄 Complete API Flow Example

### Upload Phase (Admin)
```
1. POST /admin/upload
   ├─ pdfplumber reads PDF
   ├─ re finds questions
   ├─ SentenceTransformer creates embeddings
   ├─ FAISS builds index
   └─ DataManager saves everything
```

### Query Phase (Client)
```
1. GET /ask?q=question
   ├─ re understands intent
   ├─ SentenceTransformer creates query embedding
   ├─ FAISS finds similar chunks
   ├─ Groq generates answer
   ├─ re cleans response
   └─ FastAPI returns clean answer
```

---

## 🛠️ Error Handling

### Common Errors and Solutions

#### PDF Upload Errors
```json
{
  "error": "Only PDF files are allowed"
}
```
**Solution**: Upload only `.pdf` files

```json
{
  "error": "No text could be extracted from PDF"
}
```
**Solution**: Check if PDF has readable text (not scanned images)

#### Query Errors
```json
{
  "error": "No PDF data available. Admin needs to upload a PDF first."
}
```
**Solution**: Admin must upload a PDF first

```json
{
  "error": "FAISS index not found. Admin needs to re-upload PDF."
}
```
**Solution**: Re-upload the PDF to recreate the index

---

## 📊 Performance Notes

### Speed Optimization
- **FAISS search**: ~1-5 milliseconds per query
- **Embedding creation**: ~50-100ms per document
- **AI response**: ~500-2000ms depending on complexity

### Memory Usage
- **Embeddings**: ~1MB per 1000 chunks
- **FAISS Index**: ~2MB per 1000 chunks
- **Text Storage**: ~10KB per question

---

## 🔧 Testing the API

### Using curl
```bash
# Upload PDF
curl -X POST "http://localhost:8000/admin/upload" -F "file=@test.pdf"

# Ask question
curl "http://localhost:8000/ask?q=how%20do%20I%20reset%20password"

# Check status
curl "http://localhost:8000/admin/status"
```

### Using Python
```python
import requests

# Upload PDF
files = {'file': open('test.pdf', 'rb')}
response = requests.post('http://localhost:8000/admin/upload', files=files)

# Ask question
response = requests.get('http://localhost:8000/ask', params={'q': 'reset password'})
print(response.json())
```

### Using Frontend
Open `frontend.html` in your browser for a user-friendly interface!

---

## 🎯 Best Practices

### For Admins
1. **Use clear question formatting**: "Question 1: Answer..."
2. **Organize topics**: Group related questions together
3. **Regular updates**: Keep PDFs current with latest information

### For Developers
1. **Handle errors gracefully**: Always check for error responses
2. **Rate limiting**: Consider adding rate limits for production
3. **Monitoring**: Log API calls for debugging

### For Users
1. **Natural language**: Ask questions normally
2. **Be specific**: More specific questions get better answers
3. **Try variations**: If one query doesn't work, try rephrasing

---

## 🚀 Advanced Usage

### Custom Prompts
You can modify the prompt in `/ask` endpoint to change the AI's behavior:
- More formal tone for business use
- More casual tone for friendly support
- Different languages for international use

### Different Models
Change the Groq model in the code:
- `llama-3.3-70b-versatile` (default, balanced)
- `mixtral-8x7b-32768` (faster, simpler)
- `gemma-7b-it` (small, quick responses)

### Scalability
For high-traffic deployments:
- Use Redis for caching common queries
- Implement connection pooling for database
- Add load balancer for multiple server instances
