import pytesseract
from PIL import Image
import io

# अगर Termux में Tesseract का पाथ एरर आए, तो नीचे वाली लाइन से # हटा दें:
# pytesseract.pytesseract.tesseract_cmd = '/data/data/com.termux/files/usr/bin/tesseract'

def extract_text_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # इंग्लिश और हिंदी दोनों के लिए कोशिश करेगा (अगर हिंदी पैक इंस्टाल है)
        text = pytesseract.image_to_string(image, lang='eng')
        return text
    except Exception as e:
        return f"Error: {str(e)}. (Check if Tesseract is installed in Termux: pkg install tesseract)"

def image_to_pdf(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format="PDF")
        return pdf_bytes.getvalue()
    except Exception as e:
        return None
      
