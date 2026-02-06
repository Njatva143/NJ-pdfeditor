import fitz  # PyMuPDF
import os

class PDFHandler:
    def __init__(self, file_stream):
        self.doc = fitz.open(stream=file_stream, filetype="pdf")
        self.is_encrypted = self.doc.is_encrypted

    def get_page_count(self):
        return self.doc.page_count

    def get_page_image(self, page_num):
        page = self.doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        return pix.tobytes()

    def get_raw_text(self, page_num):
        page = self.doc.load_page(page_num)
        return page.get_text("text")

    def save_pdf(self):
        return self.doc.tobytes()

    def search_and_replace(self, page_num, search_text, replace_text, font_path=None, font_size=11, align="Left"):
        page = self.doc.load_page(page_num)
        hits = page.search_for(search_text)
        
        if not hits:
            return False, 0

        # --- FIX: FONT LOADING LOGIC ---
        if font_path:
            # Custom Font (Hindi/Other)
            font_name = "custom_font"
            
            # 1. Page par register karein (Likhaayi ke liye)
            page.insert_font(fontname=font_name, fontfile=font_path, fontbuffer=None)
            
            # 2. Font Object banayein (Length napne ke liye - Yahan Error tha)
            calc_font = fitz.Font(fontfile=font_path)
        else:
            # Standard Font (English)
            font_name = "helv"
            calc_font = fitz.Font("helvetica")

        for rect in hits:
            # 1. Purana text chupao (White Sticker)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)

            # 2. Text Width Calculate karo (Ab ye sahi chalega)
            try:
                text_len = calc_font.text_length(replace_text, fontsize=font_size)
            except:
                # Agar koi error aaye to fallback calculation
                text_len = len(replace_text) * (font_size * 0.6)

            box_width = rect.x1 - rect.x0
            
            # 3. Alignment Math
            text_x = rect.x0  # Default Left
            text_y = rect.y1 - 2  # Baseline adjust

            if align == "Center":
                text_x = rect.x0 + (box_width - text_len) / 2
            
            elif align == "Right":
                text_x = rect.x1 - text_len

            # 4. Naya Text Likho
            page.insert_text(
                (text_x, text_y),
                replace_text,
                fontname=font_name,
                fontsize=font_size,
                color=(0, 0, 0)
            )

        return True, len(hits)
        
