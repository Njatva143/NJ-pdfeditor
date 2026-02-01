import fitz  # PyMuPDF
import io

class PDFHandler:
    def __init__(self, file_stream):
        # फाइल को मेमोरी से पढ़ना
        self.doc = fitz.open(stream=file_stream, filetype="pdf")

    def get_page_count(self):
        return len(self.doc)

    def get_page_image(self, page_num):
        # पेज को इमेज में बदलना (Preview के लिए)
        page = self.doc[page_num]
        pix = page.get_pixmap()
        return pix.tobytes()

    def search_and_replace(self, page_num, search_text, replace_text):
        page = self.doc[page_num]
        hits = page.search_for(search_text)
        
        if hits:
            for rect in hits:
                # 1. पुराना टेक्स्ट छुपाओ (Redact)
                page.draw_rect(rect, color=fitz.pdfcolor["white"], fill=fitz.pdfcolor["white"])
                # 2. नया टेक्स्ट लिखो (Overlay)
                page.insert_text((rect.x0, rect.y1 - 2), replace_text, fontsize=11, color=(0, 0, 0))
            return True, len(hits)
        return False, 0

    def save_pdf(self):
        output_buffer = io.BytesIO()
        self.doc.save(output_buffer)
        return output_buffer.getvalue()
      
