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
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # High Quality
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

        # Font setup
        font_name = "helv"  # Default
        if font_path:
            font_name = "custom_font"
            page.insert_font(fontname=font_name, fontfile=font_path, fontbuffer=None)

        for rect in hits:
            # 1. Purana text chupao (White Sticker)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)

            # 2. Text Width Calculate karo (Alignment ke liye)
            text_len = fitz.get_text_length(replace_text, fontname=font_name, fontsize=font_size)
            box_width = rect.x1 - rect.x0
            
            # 3. Coordinate Math (Left/Center/Right)
            text_x = rect.x0  # Default Left
            text_y = rect.y1 - 2  # Thoda upar baseline adjust karne ke liye

            if align == "Center":
                # Formula: Start + (BoxWidth - TextWidth) / 2
                text_x = rect.x0 + (box_width - text_len) / 2
            
            elif align == "Right":
                # Formula: End - TextWidth
                text_x = rect.x1 - text_len

            # 4. Naya Text Likho
            page.insert_text(
                (text_x, text_y),
                replace_text,
                fontname=font_name,
                fontsize=font_size,
                color=(0, 0, 0) # Black Color
            )

        return True, len(hits)
        
