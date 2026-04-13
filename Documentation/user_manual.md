# NexusAI: User Manual & API Guide

Welcome to the NexusAI Customer Support Platform. This guide will walk you through setting up your AI-powered assistant and deploying it to your business website.

---

## 🏗️ Step 1: Account Setup
1. **Register**: Go to the **Register** page and create your account using your email and a secure password.
2. **Login**: Once registered, sign in to access your private **Admin Dashboard**.

---

## 📄 Step 2: Preparing Your Knowledge Base
To give your AI the "knowledge" it needs to answer customer questions, you must provide a PDF file.

### 💡 The "CS01" Standard Format
For the best results, your PDF should follow the structure seen in your sample (`CS01.pdf`):

```text
Question 1: [The Customer's Question]
Answer: [Your Company's Official Response]

Question 2: [Next Question]
Answer: [Next Response]
```

> [!TIP]
> **Pro Tip**: Use clear headings and avoid mixing many topics in one paragraph. Keeping each question and answer distinct makes your AI much more accurate.

---

## 📤 Step 3: Uploading & Training
1. Go to the **Knowledge Base Management** section in your dashboard.
2. Click **Click to select PDF** and choose your formatted FAQ file.
3. Click **Upload Knowledge Base**.
4. The system will automatically:
   - Read your document.
   - Break it into meaning-based "chunks".
   - Create AI Embeddings for lightning-fast searching.

---

## 🧪 Step 4: Internal Testing (Preview)
Before you give the chatbot to your customers, use the **Chat** page in the dashboard.
*   **Purpose**: This allows you to verify if the AI is answering correctly based on your uploaded file.
*   **Checking Logic**: If the response isn't what you expected, update your PDF format and re-upload.

---

## ⚡ Step 5: External Deployment (The Chat API)
Once you are happy with the responses, you can integrate this bot into your company's own website.

### 🛠️ Finding your API Key (Widget ID)
In the **My Knowledge Bases** table, you will see a unique **API Key** for every file you upload. This is your "Widget ID."

### 🌐 How to use the API
You can call the AI from any external website using a simple `GET` or `POST` request.

**Endpoint**: `http://localhost:8000/ask/{your_api_key}?q={your_question}`

#### **Example Integration (JavaScript/Frontend)**
```javascript
async function getAIResponse(userQuestion) {
  const apiKey = "YOUR_WIDGET_ID_FROM_DASHBOARD";
  const url = `http://localhost:8000/ask/${apiKey}?q=${encodeURIComponent(userQuestion)}`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  console.log("AI Answer:", data.answer);
  return data.answer;
}
```

#### **Example Integration (Python/Backend)**
```python
import requests

api_key = "YOUR_WIDGET_ID"
question = "How can I reset my password?"
url = f"http://localhost:8000/ask/{api_key}"

response = requests.get(url, params={"q": question})
print(response.json()['answer'])
```

---

## 🛡️ Best Practices for API Key Security
- **Confidentiality**: Your API Key is unique to your file. Keep it secret if you only want your specific users to access it.
- **Rate Limiting**: Our engine is designed for high-speed support, but ensure you aren't spamming the API from your frontend.

---

## 🆘 Troubleshooting Common Doubts
- **"Invalid API Key"**: Make sure you copied the full key from your dashboard and that you haven't deleted the file.
- **"I don't know" Answer**: Ensure the answer to the question actually exists in your uploaded PDF.
- **"Network Error"**: Verify that the backend server is running on `port 8000`.
