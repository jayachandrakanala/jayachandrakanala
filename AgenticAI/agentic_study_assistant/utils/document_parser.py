import io
from pypdf import PdfReader
from docx import Document

def parse_uploaded_file(uploaded_file) -> str:
    """Extracts raw text content from PDF, DOCX, or TXT file."""
    filename = uploaded_file.name.lower()
    text = ""
    
    if filename.endswith(".pdf"):
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
                
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(uploaded_file.read()))
        for para in doc.paragraphs:
            text += para.text + "\n"
            
    elif filename.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
        
    else:
        raise ValueError("Unsupported file format! Please upload PDF, DOCX, or TXT.")
        
    return text.strip()