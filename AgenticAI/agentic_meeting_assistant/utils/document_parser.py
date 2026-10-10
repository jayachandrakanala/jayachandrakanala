import pypdf
import docx

def parse_uploaded_file(uploaded_file) -> str:
    """
    Extracts text from uploaded PDF, DOCX, or TXT transcript files.
    """
    try:
        filename = uploaded_file.name.lower()
        
        if filename.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")
            
        elif filename.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            return extracted_text
            
        elif filename.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs if para.text])
            
        else:
            return ""
    except Exception as e:
        print(f"Error parsing document: {e}")
        return ""