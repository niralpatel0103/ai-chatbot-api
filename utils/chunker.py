import re

def chunk_text(documents):
    chunks = []
    
    # Combine all documents first to handle questions spanning pages
    full_text = ""
    page_mapping = []
    
    for doc in documents:
        text = doc["text"]
        page = doc["page"]
        # Track which page each character belongs to
        start_pos = len(full_text)
        full_text += text + " "
        end_pos = len(full_text)
        page_mapping.append({
            "start": start_pos,
            "end": end_pos,
            "page": page
        })

    # Split by questions on the full text
    pattern = r"(?i)(question\s*\d+[\s\:\.\-\)]+.*?)(?=question\s*\d+[\s\:\.\-\)]+|$)"
    matches = re.finditer(pattern, full_text, re.DOTALL)

    for match in matches:
        question_text = match.group(1).strip()
        
        # Find which page this question belongs to (use first character position)
        question_start = match.start()
        question_page = 1  # default
        
        for mapping in page_mapping:
            if mapping["start"] <= question_start < mapping["end"]:
                question_page = mapping["page"]
                break

        # Only add non-empty questions
        if len(question_text) > 20:  # Filter out too short fragments
            chunks.append({
                "content": question_text,
                "page": question_page
            })

    return chunks