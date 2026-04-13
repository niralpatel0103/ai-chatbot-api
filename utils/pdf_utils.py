import pdfplumber

def extract_text_from_pdf(file_path):
    documents = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text:
                # 🔥 CLEAN TEXT
                text = text.replace("\n", " ")
                text = " ".join(text.split())  # remove extra spaces

                documents.append({
                    "page": i + 1,
                    "text": text
                })

    return documents