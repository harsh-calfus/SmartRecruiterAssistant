import pdfplumber
import docx
import re

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def parse_resume_text(text):
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.findall(r'\+?\d[\d\-\(\) ]{8,}\d', text)
    skills = [skill for skill in ["Python", "Java", "SQL", "Django", "AWS"]
              if skill.lower() in text.lower()]
    experience = max([int(num) for num in re.findall(r'(\d+)\s+years?', text)] or [0])
    return {
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "skills": skills,
        "experience": experience
    }