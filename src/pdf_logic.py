import fitz  # PyMuPDF
import io
import os
from PIL import Image, ImageDraw, ImageFont

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

    def create_text_sticker(self, text, font_path, font_size):
        try:
            if not text.strip(): # अगर टेक्स्ट खाली है तो कुछ मत बनाओ
                return None, 0, 0
                
            scale_factor = 3
            pil_font = ImageFont.truetype(font_path, font_size * scale_factor)
            
            dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
            bbox = dummy_draw.textbbox((0, 0), text, font=pil_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if text_width == 0 or text_height == 0:
                return None, 0, 0

            img = Image.new("RGBA", (text_width, text_height + 10), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Text को थोड़ा नीचे शिफ्ट किया है ताकि कटे नहीं
            draw.text((-bbox[0], 0), text, font=pil_font, fill="black")
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            
            return img_byte_arr.getvalue(), text_width / scale_factor, text_height / scale_factor
        except Exception as e:
            print(f"Font Error: {e}")
            return None, 0, 0

    def search_and_replace(self, page_num, search_text, replace_text, font_path=None, font_size=11):
        page = self.doc[page_num]
        hits = page.search_for(search_text, quads=True)
        
        if hits:
            use_sticker_mode = False
            if font_path and os.path.exists(font_path):
                use_sticker_mode = True

            for quad in hits:
                # 1. पुराना टेक्स्ट छुपाना
                page.draw_rect(quad.rect, color=fitz.pdfcolor["white"], fill=fitz.pdfcolor["white"])
                
                # 2. नया टेक्स्ट लिखना
                if use_sticker_mode:
                    img_bytes, w, h = self.create_text_sticker(replace_text, font_path, font_size)
                    
                    # ✅ FIX: यहाँ चेक लगाया है कि width और height 0 से बड़ी हो
                    if img_bytes and w > 0 and h > 0:
                        rect = fitz.Rect(quad.ul.x, quad.ul.y, quad.ul.x + w, quad.ul.y + h)
                        page.insert_image(rect, stream=img_bytes)
                else:
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
        
