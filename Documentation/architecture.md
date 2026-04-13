# Project Architecture - How Everything Works Together

## 🏗️ System Architecture Overview

Think of this system like a smart library with a super-librarian who can instantly find and explain any book content!

---

## 📊 Data Flow Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PDF File  │───▶│  pdfplumber │───▶│     re      │───▶│  Chunks     │
│             │    │   (Reader)  │    │ (Pattern)   │    │ (Pieces)    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Answer    │◀───│   Groq      │◀───│    FAISS    │◀───│SentenceTrans │
│  (Clean)    │    │  (AI Brain) │    │ (Search)    │    │ (Embeddings) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🔧 Component Breakdown

### 1. PDF Processing Pipeline

#### Input: PDF File
```
Example PDF content:
Question 1: How do I reset my password? 
Answer: Click the "Forgot Password" link on the login page...

Question 2: How do I update my email?
Answer: Go to Account Settings > Profile > Email...
```

#### Step 1: Text Extraction (pdfplumber)
```python
# What pdfplumber does:
Page 1: "Question 1: How do I reset my password? Answer: Click..."
Page 2: "Question 2: How do I update my email? Answer: Go to..."
```

**Library**: `pdfplumber`
**Purpose**: Reads PDF page by page
**Output**: List of pages with text content

#### Step 2: Question Extraction (re)
```python
# What regex finds:
["Question 1: How do I reset my password? Answer: Click...",
 "Question 2: How do I update my email? Answer: Go to..."]
```

**Library**: `re` (regular expressions)
**Purpose**: Finds question patterns in text
**Pattern**: `r"(?i)(question\s*\d+[\s\:\.\-\)]+.*?)(?=question\s*\d+[\s\:\.\-\)]+|$)"`

#### Step 3: Text Chunking
```python
# Resulting chunks:
[
  {"content": "Question 1: How do I reset my password? Answer: Click...", "page": 1},
  {"content": "Question 2: How do I update my email? Answer: Go to...", "page": 2}
]
```

**Purpose**: Break text into manageable pieces
**Benefit**: Better search results and faster processing

---

### 2. AI Brain Creation (Embeddings)

#### Step 4: Text to Numbers (SentenceTransformer)
```python
# What happens:
Text: "How do I reset my password?"
Vector: [0.12, -0.45, 0.78, ..., 0.23]  # 384 numbers
```

**Library**: `SentenceTransformer`
**Model**: `all-MiniLM-L6-v2`
**Purpose**: Convert text meaning into numbers
**Why**: Computers can compare numbers faster than text

#### Step 5: Vector Storage (FAISS)
```python
# FAISS creates searchable index:
Index contains: [
  [0.12, -0.45, 0.78, ...],  # Question 1 vector
  [0.34, 0.21, -0.67, ...],  # Question 2 vector
  ...
]
```

**Library**: `FAISS`
**Purpose**: Super-fast similarity search
**Method**: `IndexFlatIP` (Inner Product for cosine similarity)

---

### 3. Query Processing Pipeline

#### Input: User Question
```
User asks: "I forgot my password"
```

#### Step 6: Intent Understanding
```python
# System analyzes:
{
  "type": "faq",  # Not a counting question
  "query_terms": ["i", "forgot", "my", "password"]
}
```

**Library**: `re` (regex patterns)
**Purpose**: Understand what user wants
**Types**: "faq" or "counting"

#### Step 7: Query to Vector
```python
# Convert user question to vector:
"I forgot my password" → [0.15, -0.42, 0.81, ...]
```

**Library**: `SentenceTransformer`
**Purpose**: Convert question to same format as stored chunks

#### Step 8: Similarity Search (FAISS)
```python
# FAISS finds most similar:
[
  {"content": "Question 1: How do I reset my password? Answer: Click...", "similarity": 0.89},
  {"content": "Question 4: Why is my account locked? Answer: Multiple failed attempts...", "similarity": 0.67},
  {"content": "Question 18: Login issues? Answer: Check password or reset...", "similarity": 0.54}
]
```

**Library**: `FAISS`
**Purpose**: Find most relevant chunks
**Result**: Top 3 most similar chunks

---

### 4. AI Response Generation

#### Step 9: Prompt Creation
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

Context: Question 1: How do I reset my password? Answer: Click the "Forgot Password" link...
User Query: I forgot my password"""
```

**Purpose**: Give AI clear instructions for customer support

#### Step 10: AI Generation (Groq)
```python
# AI response (before cleaning):
"Based on the provided context, you can reset your password by clicking the 'Forgot Password' link on the login page. This will send instructions to your email."
```

**Library**: `Groq`
**Model**: `llama-3.3-70b-versatile`
**Purpose**: Generate human-like response

#### Step 11: Response Cleaning
```python
# Clean response:
"You can reset your password by clicking the 'Forgot Password' link on the login page."
```

**Library**: `re` (regex)
**Purpose**: Remove robotic phrases, make it natural

---

## 🗄️ Data Storage Architecture

### File Structure
```
data/
├── questions_store.json      # Simple list of all questions
├── sections_store.json       # Structured questions with numbers
├── current_chunks.json       # Text chunks with page numbers
├── faiss_index.bin          # FAISS vector index
├── chat_history.json        # Conversation history
└── uploaded_pdfs/           # Original PDF files
```

### DataManager Class
```python
class DataManager:
    def save_questions(self, questions):      # Save to JSON
    def load_questions(self):                  # Load from JSON
    def save_faiss_index(self, index):         # Save FAISS index
    def load_faiss_index(self):                # Load FAISS index
    def save_chat_history(self, history):      # Save conversation
    def load_chat_history(self):               # Load conversation
```

**Purpose**: Handle all file operations
**Benefits**: 
- Persistent data across server restarts
- Easy backup and restore
- Admin can manage data

---

## 🔄 Request-Response Cycle

### Complete Flow for One Question

```
1. User types: "How do I reset password?"
   ↓
2. FastAPI receives GET /ask?q=How%20do%20I%20reset%20password
   ↓
3. understand_user_query() analyzes: type="faq"
   ↓
4. SentenceTransformer converts question to vector
   ↓
5. FAISS searches for similar vectors
   ↓
6. Returns top 3 most relevant chunks
   ↓
7. Groq AI generates response using chunks as context
   ↓
8. clean_response() removes unwanted phrases
   ↓
9. FastAPI returns: {"answer": "Click 'Forgot Password'...", "intent": {"type": "faq"}}
   ↓
10. User sees clean, helpful answer
```

---

## 🎯 Performance Optimization

### Speed Techniques
1. **FAISS Index**: O(log n) search time
2. **Normalized Embeddings**: Faster cosine similarity
3. **Top-K=3**: Limit results for speed
4. **File Caching**: Avoid reprocessing PDFs

### Memory Optimization
1. **Chunk Size**: Balance between detail and memory
2. **Vector Compression**: Use float32 instead of float64
3. **Lazy Loading**: Load data only when needed

### Scalability Considerations
1. **Horizontal Scaling**: Multiple server instances
2. **Database Upgrade**: PostgreSQL for multi-user
3. **CDN**: For static file serving
4. **Load Balancer**: Distribute traffic

---

## 🛡️ Error Handling Architecture

### Error Types and Handling
```python
# PDF Errors
if not file.filename.endswith('.pdf'):
    return {"error": "Only PDF files are allowed"}

# Data Errors
if not data_manager.data_exists():
    return {"error": "No PDF data available"}

# Search Errors
if not results:
    return {"answer": "Sorry, I couldn't find that information."}

# AI Errors
try:
    response = client.chat.completions.create(...)
except Exception:
    return {"answer": "Sorry, I couldn't find that information."}
```

### Graceful Degradation
- **No PDF**: Clear error message
- **Search Fails**: Fallback to simple text search
- **AI Fails**: Return generic helpful message
- **File Errors**: Try to recover or reprocess

---

## 🔍 Monitoring and Debugging

### Logging Strategy
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Processing query: {q}")
logger.info(f"Found {len(results)} relevant chunks")
logger.info(f"Generated response: {answer[:100]}...")
```

### Debug Information
- Query processing time
- Number of chunks found
- Similarity scores
- AI response time
- Error details

### Performance Metrics
- Average response time
- Success rate
- Most common queries
- Error frequency

---

## 🎨 Design Principles

### Simplicity
- **Clear separation of concerns**
- **Minimal dependencies**
- **Easy to understand code**

### Reliability
- **Graceful error handling**
- **Data persistence**
- **Consistent responses**

### Performance
- **Fast search algorithms**
- **Efficient memory usage**
- **Scalable architecture**

### Usability
- **Natural language queries**
- **Clean responses**
- **Helpful error messages**

---

## 🚀 Future Enhancements

### Possible Improvements
1. **Multi-language support**
2. **Voice input/output**
3. **Image processing**
4. **Real-time collaboration**
5. **Advanced analytics**
6. **Integration with chat platforms**

### Extension Points
- **Custom embedding models**
- **Different AI providers**
- **Alternative storage backends**
- **Additional file formats**

This architecture provides a solid foundation for a production-ready AI customer support system!
