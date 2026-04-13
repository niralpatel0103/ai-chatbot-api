from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils.pdf_utils import extract_text_from_pdf
from utils.data_manager import DataManager
import os
from dotenv import load_dotenv
from groq import Groq
from utils.chunker import chunk_text
from utils.vector_store import create_embeddings, create_faiss_index, search
import re
import json
import pdfplumber

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data manager for persistence
data_manager = DataManager()

# API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API key not found. Check your .env file")

client = Groq(api_key=api_key)

def understand_user_query(query: str) -> dict:
    """
    Understand user intent (customer support focused)
    """
    query_lower = query.lower()
    
    # Only classify as counting for explicit counting queries
    counting_keywords = ["how many", "total number", "count", "number of"]
    is_counting = any(keyword in query_lower for keyword in counting_keywords)
    
    intent = {
        "type": "counting" if is_counting else "faq",
        "query_terms": query_lower.split()
    }
    
    # Detect specific question attempts (for direct question lookup)
    question_patterns = [
        r"question\s*(\d+)",
        r"q\s*(\d+)",
        r"(\d+).*question",
        r"question.*(\d+)",
        r"(\d+)(?:st|nd|rd|th)?\s*question"
    ]
    
    for pattern in question_patterns:
        match = re.search(pattern, query_lower)
        if match:
            intent["type"] = "faq"
            intent["question_number"] = int(match.group(1))
            break
    
    return intent

def clean_response(response_text):
    """Clean LLM response for customer support"""
    if not response_text:
        return "Sorry, I couldn't find that information."
    
    # Remove unwanted phrases
    unwanted_phrases = [
        "Based on the provided context",
        "According to the context",
        "From the context provided",
        "Based on context",
        "According to context",
        "Question", "question", "Question", "question",
        "context", "Context",
        "retrieval", "matching", "matches"
    ]
    
    cleaned = response_text
    for phrase in unwanted_phrases:
        cleaned = cleaned.replace(phrase, "")
    
    # Remove extra whitespace and clean up
    cleaned = cleaned.strip()
    
    # Remove any numbering at start (like "1.", "2.")
    cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
    
    # If result is too short after cleaning, provide fallback
    if len(cleaned) < 10:
        return "Sorry, I couldn't find that information."
    
    return cleaned

def extract_questions_continuous(text):
    """
    Extract questions from continuous question-answer format (no sections)
    """
    # normalize text first
    text = text.replace("\n", " ")
    
    # Simple pattern for continuous questions
    pattern = r"(?i)(question\s*\d+[\s\:\.\-\)]+.*?)(?=question\s*\d+[\s\:\.\-\)]+|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    
    questions = {}
    for i, q in enumerate(matches, 1):
        q_num_match = re.search(r"question\s*(\d+)", q, re.IGNORECASE)
        if q_num_match:
            q_num = int(q_num_match.group(1))
            questions[f"Q{q_num}"] = {
                "question_num": q_num,
                "content": q.strip()
            }
    
    return questions

def analyze_document_topics(questions_dict):
    """
    Automatically detect topics present in document
    """
    all_content = "\n\n".join([q["content"] for q in questions_dict.values()])
    
    topics_found = set()
    
    # Common topic indicators
    topic_indicators = {
        "math": ["calculate", "add", "subtract", "multiply", "divide", "square", "root", "factorial", "prime", "perimeter", "area", "formula", "pi", "power", "equation", "percent", "ratio", "average"],
        "science": ["science", "physics", "chemistry", "biology", "gravity", "light", "temperature", "boiling", "freezing", "molecule", "atom", "energy", "velocity"],
        "geography": ["capital", "country", "city", "ocean", "continent", "place", "location", "map", "river", "mountain"],
        "history": ["who", "when", "invented", "discovered", "wrote", "father", "mother", "born", "history", "war", "king", "queen"],
        "computer": ["computer", "cpu", "software", "programming", "code", "algorithm", "database", "internet", "website", "app"],
        "language": ["grammar", "vocabulary", "synonym", "antonym", "sentence", "paragraph", "essay", "comprehension"],
        "business": ["business", "company", "revenue", "profit", "cost", "price", "market", "sales", "customer"],
        "health": ["medicine", "doctor", "disease", "treatment", "symptom", "health", "hospital", "drug"]
    }
    
    # Detect topics in content
    content_lower = all_content.lower()
    for topic, keywords in topic_indicators.items():
        for keyword in keywords:
            if keyword in content_lower:
                topics_found.add(topic)
                break
    
    return list(topics_found)

# ------------------ ROUTES ------------------

@app.get("/")
def home():
    return {"message": "Server running"}

@app.post("/admin/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"error": "Only PDF files are allowed"}
        
    file_path = f"data/{file.filename}"

    try:
        # Save PDF
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        documents = extract_text_from_pdf(file_path)
        
        if not documents:
            return {"error": "No text could be extracted from PDF"}

        # Get full text
        full_text = "\n".join([doc["text"] for doc in documents])
        
        if len(full_text.strip()) < 50:
            return {"error": "PDF appears to be empty or contains no readable text"}

        # Extract questions (continuous format)
        questions_dict = extract_questions_continuous(full_text)
        
        # Also maintain simple list for backward compatibility
        questions_store = [q["content"] for q in questions_dict.values()]
        
        # Analyze document topics
        document_topics = analyze_document_topics(questions_dict)
        
        if not questions_dict:
            return {"error": "No questions found in PDF. Ensure document contains questions formatted as 'Question X: Answer...'"}

        # Chunking
        chunks = chunk_text(documents)
        
        if not chunks:
            return {"error": "Failed to create chunks from document"}

        # Save chunks to file
        chunk_file_path = f"data/{file.filename}_chunks.json"
        with open(chunk_file_path, "w") as f:
            json.dump(chunks, f, indent=2)

        # Embeddings + FAISS
        embeddings = create_embeddings(chunks)
        index = create_faiss_index(embeddings)

        # Save all data using data manager
        data_manager.save_questions(questions_store)
        data_manager.save_sections(questions_dict)
        data_manager.save_chunks(chunks)
        data_manager.save_faiss_index(index)
        data_manager.clear_chat_history()  # Clear chat when new PDF uploaded

        return {
            "message": "PDF processed and stored successfully",
            "total_chunks": len(chunks),
            "total_questions_extracted": len(questions_dict),
            "document_topics": document_topics,  # New: detected topics
            "chunks_saved_at": chunk_file_path,
            "ready_for_clients": True
        }
        
    except Exception as e:
        return {"error": f"Error processing PDF: {str(e)}"}

# ------------------ ADMIN ENDPOINTS ------------------

@app.get("/admin/status")
def admin_status():
    """Check system status and uploaded files"""
    return {
        "data_exists": data_manager.data_exists(),
        "uploaded_files": data_manager.get_uploaded_files(),
        "chat_history_length": len(data_manager.load_chat_history())
    }

@app.get("/admin/clear-chat")
def admin_clear_chat():
    """Clear chat history"""
    data_manager.clear_chat_history()
    return {"message": "Chat history cleared by admin"}

@app.get("/admin/questions")
def admin_get_questions():
    """Get all extracted questions for admin review"""
    questions_dict = data_manager.load_sections()  # Loading questions dict from sections storage
    document_topics = analyze_document_topics(questions_dict)
    return {
        "total_questions": len(questions_dict),
        "document_topics": document_topics,
        "questions": questions_dict
    }

# ------------------ CLIENT ENDPOINTS ------------------

@app.get("/ask")
def ask_question(q: str):
    """Customer support Q&A endpoint"""
    if not data_manager.data_exists():
        return {"error": "No PDF data available. Admin needs to upload a PDF first."}

    # Load data
    questions_store = data_manager.load_questions()
    questions_dict = data_manager.load_sections()
    chunks_store = data_manager.load_chunks()
    index_store = data_manager.load_faiss_index()

    if not index_store:
        return {"error": "FAISS index not found. Admin needs to re-upload PDF."}

    # Understand intent
    intent = understand_user_query(q)
    
    # Handle specific question lookup
    if intent["type"] == "faq" and intent.get("question_number"):
        q_key = f"Q{intent['question_number']}"
        if q_key in questions_dict:
            answer = clean_response(questions_dict[q_key]["content"])
            return {
                "answer": answer,
                "intent": {"type": "faq"}
            }
        else:
            return {
                "answer": "Sorry, I couldn't find that question.",
                "intent": {"type": "faq"}
            }
    
    # Handle counting queries
    if intent["type"] == "counting":
        all_questions_text = "\n\n".join([q["content"] for q in chunks_store])
        
        prompt = f"""You are a customer support assistant.
Answer user's question using provided context.
Rules:
Give a direct answer only
Do NOT explain reasoning
Do NOT mention context
Do NOT mention question numbers
Keep the answer short and clear
If answer is not found, say: 'Sorry, I couldn't find that information.'

Context:
{all_questions_text}

User Query: {q}"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = clean_response(response.choices[0].message.content.strip())
            return {
                "answer": answer,
                "intent": {"type": "counting"}
            }
        except Exception:
            return {
                "answer": "Sorry, I couldn't find that information.",
                "intent": {"type": "counting"}
            }
    
    # Handle general FAQ queries
    try:
        results = search(q, index_store, chunks_store, k=3)
        
        if not results:
            return {
                "answer": "Sorry, I couldn't find that information.",
                "intent": {"type": "faq"}
            }
        
        context = "\n\n".join([r["content"] for r in results])
        
        prompt = f"""You are a customer support assistant.
Answer user's question using provided context.
Rules:
Give a direct answer only
Do NOT explain reasoning
Do NOT mention context
Do NOT mention question numbers
Keep the answer short and clear
If answer is not found, say: 'Sorry, I couldn't find that information.'

Context:
{context}

User Query: {q}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = clean_response(response.choices[0].message.content.strip())
        
        return {
            "answer": answer,
            "intent": {"type": "faq"}
        }
        
    except Exception:
        return {
            "answer": "Sorry, I couldn't find that information.",
            "intent": {"type": "faq"}
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
