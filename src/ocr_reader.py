import pytesseract
from PIL import Image
import PyPDF2

def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    else:
        img = Image.open(file)
        return pytesseract.image_to_string(img)
