import re

def extract_qa_pairs(text):
    qa_pairs = []

    # Simple pattern: Question X ... Answer ...
    pattern = r"(Question\s*\d+.*?)(Answer\s*[:\-].*?)(?=Question\s*\d+|$)"

    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    for i, (q, a) in enumerate(matches):
        qa_pairs.append({
            "id": i + 1,
            "question": q.strip(),
            "answer": a.strip()
        })

    return qa_pairs