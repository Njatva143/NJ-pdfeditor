import fitz  # PyMuPDF
import io
import os

class PDFHandler:
    def __init__(self, file_stream):
        self.doc = fitz.open(stream=file_stream, filetype="pdf")

    @property
    def is_encrypted(self):
        """Check if PDF is password protected"""
        if self.doc.is_encrypted:
            if self.doc.authenticate(""):
                return False
            return True
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

    def search_and_replace(self, page_num, search_text, replace_text, font_path=None):
        page = self.doc[page_num]
        hits = page.search_for(search_text, quads=True)
        
        if hits:
            # Font Logic: Agar Hindi font diya hai to use load karein
            font_name = "helv" # Default English
            if font_path and os.path.exists(font_path):
                font_name = "custom_font"
                # Font ko PDF page par register karna
                page.insert_font(fontname=font_name, fontfile=font_path, fontbuffer=None)

            for quad in hits:
                # 1. Purana text chupana
                page.draw_rect(quad.rect, color=fitz.pdfcolor["white"], fill=fitz.pdfcolor["white"])
                
                # 2. Naya text likhna
                page.insert_text(
                    (quad.ul.x, quad.ul.y + 10),
                    replace_text,
                    fontname=font_name,
                    fontsize=11,
                    color=(0, 0, 0)
                )
            return True, len(hits)
        return False, 0

    def save_pdf(self):
        output_buffer = io.BytesIO()
        self.doc.save(output_buffer)
        return output_buffer.getvalue()
        
