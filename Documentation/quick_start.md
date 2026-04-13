# Quick Start Guide - Get Running in 5 Minutes

## 🚀 Super Quick Setup

### Step 1: Install Everything
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all libraries
pip install fastapi uvicorn pdfplumber sentence-transformers faiss-cpu groq python-dotenv
```

### Step 2: Get API Key
1. Go to [Groq Console](https://console.groq.com)
2. Sign up for free account
3. Copy your API key
4. Create `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

### Step 3: Start Server
```bash
uvicorn main_fixed:app --reload
```

### Step 4: Test It!
Open your browser and go to `http://localhost:8000` - you should see:
```json
{"message": "Server running"}
```

---

## 📱 Using the System

### Method 1: Web Interface
1. Open `frontend.html` in your browser
2. Upload a PDF with questions and answers
3. Start asking questions!

### Method 2: Direct API
```bash
# Upload PDF
curl -X POST "http://localhost:8000/admin/upload" -F "file=@your_faq.pdf"

# Ask question
curl "http://localhost:8000/ask?q=how%20do%20I%20reset%20password"
```

---

## 🧪 Test with Sample Data

### Create a Test PDF
Create a simple text file with this content and save as `test.pdf`:

```
Question 1: How do I reset my password? 
Answer: Click the "Forgot Password" link on the login page and follow the email instructions.

Question 2: How do I update my email address?
Answer: Go to Account Settings > Profile > Email and enter your new email address.

Question 3: What if I forgot my username?
Answer: Use your registered email address to recover your username on the login page.
```

### Upload and Test
```bash
# Upload the test PDF
curl -X POST "http://localhost:8000/admin/upload" -F "file=@test.pdf"

# Try these questions:
curl "http://localhost:8000/ask?q=forgot%20password"
curl "http://localhost:8000/ask?q=change%20email"
curl "http://localhost:8000/ask?q=lost%20username"
curl "http://localhost:8000/ask?q=how%20many%20questions"
```

---

## 🔧 Troubleshooting

### Common Issues

#### "API key not found"
**Problem**: Missing `.env` file or wrong API key
**Solution**: 
1. Create `.env` file in project root
2. Add: `GROQ_API_KEY=your_actual_key`

#### "ModuleNotFoundError"
**Problem**: Missing libraries
**Solution**: 
```bash
pip install fastapi uvicorn pdfplumber sentence-transformers faiss-cpu groq python-dotenv
```

#### "No text could be extracted from PDF"
**Problem**: PDF is scanned images or corrupted
**Solution**: Use PDF with actual text, not images

#### "Server not responding"
**Problem**: Wrong port or server not running
**Solution**: 
```bash
# Kill any existing processes
pkill -f uvicorn

# Start fresh
uvicorn main_fixed:app --reload --port 8000
```

---

## 📊 Quick Test Results

You should see responses like:

```json
{
  "answer": "Click the 'Forgot Password' link on the login page and follow the email instructions.",
  "intent": {
    "type": "faq"
  }
}
```

For counting questions:
```json
{
  "answer": "There are 3 questions in the document.",
  "intent": {
    "type": "counting"
  }
}
```

---

## 🎯 What Makes This Special?

1. **Natural Language**: Ask questions normally
2. **Fast Responses**: Answers in seconds
3. **Clean Output**: No robotic explanations
4. **Any Domain**: Works with any FAQ document
5. **Easy Setup**: Running in minutes

---

## 📚 Next Steps

Once you have it running:
1. **Read the full documentation** in the Documentation folder
2. **Try different PDFs** with your own content
3. **Customize the responses** by modifying prompts
4. **Integrate with your website** using the API

---

## 🆘 Need Help?

If something doesn't work:
1. Check the [full documentation](README.md)
2. Look at [API guide](api_guide.md)
3. Review [architecture](architecture.md)

Still stuck? The system is designed to be simple - most issues are:
- Missing API key
- Wrong PDF format
- Network/firewall issues

Happy coding! 🎉
