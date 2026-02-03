import fitz  # PyMuPDF
import io
import os
from PIL import Image, ImageDraw, ImageFont  # ✅ New imports for Hindi Sticker

class PDFHandler:
    def __init__(self, file_stream):
        self.doc = fitz.open(stream=file_stream, filetype="pdf")

    @property
    def is_encrypted(self):
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

    # 👇👇👇 MAGIC FUNCTION: Hindi Text ko Image banakar chipkana 👇👇👇
    def create_text_sticker(self, text, font_path, font_size):
        try:
            # 1. High Quality ke liye font size 3x bada karein
            scale_factor = 3 
            pil_font = ImageFont.truetype(font_path, font_size * scale_factor)
            
            # 2. Text ka size naapein (Calculate Size)
            dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
            bbox = dummy_draw.textbbox((0, 0), text, font=pil_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 3. Transparent Canvas banayein
            img = Image.new("RGBA", (text_width, text_height + 10), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # 4. Hindi Text Likhein (Black Color)
            draw.text((-bbox[0], 0), text, font=pil_font, fill="black")
            
            # 5. Image ko Bytes mein convert karein
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            
            # PDF coordinates ke liye wapas normal size return karein
            return img_byte_arr.getvalue(), text_width / scale_factor, text_height / scale_factor
        except Exception as e:
            print(f"Font Error: {e}")
            return None, 0, 0

    def search_and_replace(self, page_num, search_text, replace_text, font_path=None, font_size=11):
        page = self.doc[page_num]
        hits = page.search_for(search_text, quads=True)
        
        if hits:
            # Check karein ki kya user ne Hindi Font diya hai?
            use_sticker_mode = False
            if font_path and os.path.exists(font_path):
                # Agar font hai, to hum "Sticker Mode" use karenge
                use_sticker_mode = True

            for quad in hits:
                # 1. Purana text chupana (White Tape)
                page.draw_rect(quad.rect, color=fitz.pdfcolor["white"], fill=fitz.pdfcolor["white"])
                
                # 2. Naya Text Likhna/Chipkana
                if use_sticker_mode:
                    # ✅ HINDI MODE: Image banakar chipkao
                    img_bytes, w, h = self.create_text_sticker(replace_text, font_path, font_size)
                    if img_bytes:
                        # Image insert karne ke liye Rect banayein
                        # (x, y, x+width, y+height)
                        rect = fitz.Rect(quad.ul.x, quad.ul.y, quad.ul.x + w, quad.ul.y + h)
                        page.insert_image(rect, stream=img_bytes)
                else:
                    # ❌ ENGLISH MODE: Normal text (purana tarika)
                    page.insert_text(
                        (quad.ul.x, quad.ul.y + 10),
                        replace_text,
                        fontname="helv",
                        fontsize=font_size,
                        color=(0, 0, 0)
                    )
            return True, len(hits)
        return False, 0

    def save_pdf(self):
        output_buffer = io.BytesIO()
        self.doc.save(output_buffer)
        return output_buffer.getvalue()
        
