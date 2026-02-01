import fitz  # PyMuPDF
import io

class PDFHandler:
    def __init__(self, file_stream):
        # फाइल को मेमोरी में खोलना
        self.doc = fitz.open(stream=file_stream, filetype="pdf")

    @property
    def is_encrypted(self):
        """चेक करें कि क्या PDF में पासवर्ड लगा है"""
        if self.doc.is_encrypted:
            # कोशिश करें कि क्या यह बिना पासवर्ड के खुल सकती है?
            if self.doc.authenticate(""):
                return False # खुल गई (पासवर्ड नहीं था)
            return True # अभी भी लॉक है
        return False

    def get_page_count(self):
        return len(self.doc)

    def get_page_image(self, page_num):
        page = self.doc[page_num]
        pix = page.get_pixmap()
        return pix.tobytes()

    def get_raw_text(self, page_num):
        page = self.doc[page_num]
        return page.get_text("text")

    def search_and_replace(self, page_num, search_text, replace_text):
        page = self.doc[page_num]
        hits = page.search_for(search_text, quads=True)
        
        if hits:
            for quad in hits:
                page.draw_rect(quad.rect, color=fitz.pdfcolor["white"], fill=fitz.pdfcolor["white"])
                page.insert_text((quad.ul.x, quad.ul.y + 10), replace_text, fontsize=11, color=(0, 0, 0))
            return True, len(hits)
        return False, 0

    def save_pdf(self):
        output_buffer = io.BytesIO()
        self.doc.save(output_buffer)
        return output_buffer.getvalue()
        
