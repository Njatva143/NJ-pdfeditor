import streamlit as st
import io
import tempfile
import numpy as np
from streamlit_drawable_canvas import st_canvas
from pdf2image import convert_from_bytes
from PIL import Image, ImageFont, ImageDraw
from pdf2docx import Converter
from docx import Document

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Nj PDF Editor",
    layout="wide",
    page_icon="📄"
)

st.markdown("""
<style>
.big-title {
    font-size:32px !important;
    font-weight:700;
}
.toolbar-box {
    padding:15px;
    border-radius:10px;
    background-color:#f2f2f2;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">📄 Nj PDF Live Editor</p>', unsafe_allow_html=True)

DPI = 150
CANVAS_WIDTH = 850

# ----------------------------
# UTILITIES
# ----------------------------

def pdf_to_images(file_bytes):
    return convert_from_bytes(file_bytes, dpi=DPI)

def resize_img(img):
    ratio = CANVAS_WIDTH / img.width
    return img.resize((CANVAS_WIDTH, int(img.height * ratio)))

def save_pdf(pages_list):
    buf = io.BytesIO()
    rgb_pages = [p.convert("RGB") for p in pages_list]
    rgb_pages[0].save(buf, format="PDF", save_all=True, append_images=rgb_pages[1:])
    return buf.getvalue()

# ----------------------------
# SESSION STATE
# ----------------------------

if "pages" not in st.session_state:
    st.session_state.pages = []

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# ----------------------------
# SIDEBAR
# ----------------------------

st.sidebar.title("⚙️ Settings")

language = st.sidebar.selectbox("🌐 Language", ["English", "Hindi"])

mode = st.sidebar.radio("Mode", ["Live Editor", "PDF → Word"])

# ----------------------------
# LIVE EDITOR
# ----------------------------

if mode == "Live Editor":

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded:

        if st.session_state.file_name != uploaded.name:
            st.session_state.file_name = uploaded.name
            st.session_state.canvas_key = 0
            st.session_state.pages = pdf_to_images(uploaded.read())

        if st.session_state.pages:

            page_index = st.number_input(
                "Page",
                min_value=1,
                max_value=len(st.session_state.pages),
                value=1
            ) - 1

            img = st.session_state.pages[page_index].convert("RGB")
            bg_img = resize_img(img)

            st.markdown('<div class="toolbar-box">', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                tool = st.selectbox("Tool", ["Move", "Draw", "Text", "Rectangle"])

            with col2:
                stroke = st.slider("Size", 1, 30, 5)

            with col3:
                color = st.color_picker("Color", "#000000")

            st.markdown('</div>', unsafe_allow_html=True)

            drawing_mode = {
                "Move": "transform",
                "Draw": "freedraw",
                "Text": "text",
                "Rectangle": "rect"
            }[tool]

            canvas = st_canvas(
                fill_color="rgba(0,0,0,0)",
                stroke_width=stroke,
                stroke_color=color,
                background_image=bg_img,
                height=bg_img.height,
                width=bg_img.width,
                drawing_mode=drawing_mode,
                update_streamlit=True,
                key=f"canvas_{st.session_state.canvas_key}"
            )

            colA, colB = st.columns(2)

            with colA:
                if st.button("✅ Apply Changes"):
                    if canvas.image_data is not None:
                        fg = Image.fromarray(
                            canvas.image_data.astype("uint8")
                        ).convert("RGBA")

                        bg = img.convert("RGBA")
                        fg = fg.resize(bg.size)

                        merged = Image.alpha_composite(bg, fg).convert("RGB")

                        st.session_state.pages[page_index] = merged
                        st.session_state.canvas_key += 1
                        st.success("Saved!")
                        st.rerun()

            with colB:
                if st.button("📥 Download PDF"):
                    pdf_bytes = save_pdf(st.session_state.pages)
                    st.download_button(
                        "Download Edited PDF",
                        pdf_bytes,
                        "nj_edited.pdf"
                    )

# ----------------------------
# PDF → WORD
# ----------------------------

elif mode == "PDF → Word":

    file = st.file_uploader("Upload PDF", type="pdf")

    if file and st.button("Convert to Word"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            pdf_path = tmp.name

        docx_path = pdf_path.replace(".pdf", ".docx")

        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()

        with open(docx_path, "rb") as f:
            st.download_button("Download Word File", f.read(), "converted.docx")
