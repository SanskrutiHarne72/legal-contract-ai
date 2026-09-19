import fitz


def extract_text_from_pdf(uploaded_file):
    filename = getattr(uploaded_file, "name", "").lower()
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if filename.endswith(".docx"):
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(full_text)
        except Exception:
            return ""

    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text() + "\n"
        pdf.close()
        return text
    except Exception:
        return ""