import json
import os
from typing import Dict, List, Optional

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.questions_file = os.path.join(data_dir, "questions_store.json")
        self.sections_file = os.path.join(data_dir, "sections_store.json")
        self.chunks_file = os.path.join(data_dir, "current_chunks.json")
        self.index_file = os.path.join(data_dir, "faiss_index.bin")
        self.chat_file = os.path.join(data_dir, "chat_history.json")
        
    def save_questions(self, questions: List[str]):
        """Save simple questions list"""
        with open(self.questions_file, 'w') as f:
            json.dump(questions, f, indent=2)
    
    def load_questions(self) -> List[str]:
        """Load simple questions list"""
        if os.path.exists(self.questions_file):
            with open(self.questions_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_sections(self, sections: Dict):
        """Save questions with sections"""
        with open(self.sections_file, 'w') as f:
            json.dump(sections, f, indent=2)
    
    def load_sections(self) -> Dict:
        """Load questions with sections"""
        if os.path.exists(self.sections_file):
            with open(self.sections_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_chunks(self, chunks: List[Dict]):
        """Save chunks"""
        with open(self.chunks_file, 'w') as f:
            json.dump(chunks, f, indent=2)
    
    def load_chunks(self) -> List[Dict]:
        """Load chunks"""
        if os.path.exists(self.chunks_file):
            with open(self.chunks_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_faiss_index(self, index):
        """Save FAISS index"""
        import faiss
        faiss.write_index(index, self.index_file)
    
    def load_faiss_index(self):
        """Load FAISS index"""
        import faiss
        if os.path.exists(self.index_file):
            return faiss.read_index(self.index_file)
        return None
    
    def save_chat_history(self, history: List[Dict]):
        """Save chat history"""
        with open(self.chat_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def load_chat_history(self) -> List[Dict]:
        """Load chat history"""
        if os.path.exists(self.chat_file):
            with open(self.chat_file, 'r') as f:
                return json.load(f)
        return []
    
    def clear_chat_history(self):
        """Clear chat history"""
        if os.path.exists(self.chat_file):
            os.remove(self.chat_file)
    
    def data_exists(self) -> bool:
        """Check if any PDF data exists"""
        return os.path.exists(self.questions_file) and os.path.exists(self.chunks_file)
    
    def get_uploaded_files(self) -> List[str]:
        """Get list of uploaded PDF files"""
        pdf_files = []
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if file.endswith('.pdf') and not file.endswith('_chunks.json'):
                    pdf_files.append(file)
        return pdf_files
