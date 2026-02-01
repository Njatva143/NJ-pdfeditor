import fitz  # PyMuPDF
import io

class PDFHandler:
    def __init__(self, file_stream):
        # फाइल को मेमोरी में खोलना
        self.doc = fitz.open(stream=file_stream, filetype="pdf")

    def get_page_count(self):
        return len(self.doc)

    def get_page_image(self, page_num):
        # पेज का प्रिव्यू इमेज बनाना
        page = self.doc[page_num]
        pix = page.get_pixmap()
        return pix.tobytes()

    def get_raw_text(self, page_num):
        # डीबगिंग के लिए: पेज का असली टेक्स्ट निकालना
        page = self.doc[page_num]
        return page.get_text("text")

    def search_and_replace(self, page_num, search_text, replace_text):
        page = self.doc[page_num]
        
        # 'quads' का इस्तेमाल सटीक लोकेशन के लिए
        hits = page.search_for(search_text, quads=True)
        
        if hits:
            for quad in hits:
                # 1. पुराना टेक्स्ट छुपाओ (Redact - White Box)
                page.draw_rect(quad.rect, color=fitz.pdfcolor["white"], fill=fitz.pdfcolor["white"])
                
                # 2. नया टेक्स्ट लिखो (Overlay)
                # Y-axis को थोड़ा एडजस्ट किया है ताकि लाइन सीधी रहे
                page.insert_text((quad.ul.x, quad.ul.y + 10), replace_text, fontsize=11, color=(0, 0, 0))
            return True, len(hits)
        return False, 0

    def save_pdf(self):
        # फाइल सेव करके डाउनलोड के लिए तैयार करना
        output_buffer = io.BytesIO()
        self.doc.save(output_buffer)
        return output_buffer.getvalue()
