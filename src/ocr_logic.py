import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io

# Tesseract ko batana padta hai ki Hindi+English dono padho
LANG_CONFIG = 'hin+eng'

def extract_text_from_file(uploaded_file):
    text_content = ""
    try:
        file_bytes = uploaded_file.getvalue()
        file_type = uploaded_file.type

        # 1. Agar Image hai (JPG, PNG)
        if "image" in file_type:
            image = Image.open(io.BytesIO(file_bytes))
            text_content = pytesseract.image_to_string(image, lang=LANG_CONFIG)

        # 2. Agar PDF hai
        elif "pdf" in file_type:
            # PDF ke har page ko image mein badlo (High Quality)
            images = convert_from_bytes(file_bytes)
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img, lang=LANG_CONFIG)
                text_content += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        else:
            return "❌ Unsupported file format. Please upload Image or PDF."

    except Exception as e:
        return f"❌ Error in OCR: {e}"
        
    return text_content
