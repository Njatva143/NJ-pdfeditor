import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO

st.set_page_config(page_title="NJ Editor", layout="wide")

# ---------------- LANGUAGE ----------------
lang = st.sidebar.selectbox("🌐 Language / भाषा", ["English", "Hindi"])

def t(en, hi):
    return en if lang == "English" else hi

st.title("📝 NJ Editor - Live PDF Editor")

# ---------------- PAGE TYPE ----------------
page_type = st.sidebar.selectbox(
    t("Select Page Size", "पेज साइज चुनें"),
    ["A4", "Letter", "Legal"]
)

page_sizes = {
    "A4": (595, 842),
    "Letter": (612, 792),
    "Legal": (612, 1008)
}

# ---------------- UPLOAD PDF ----------------
uploaded_file = st.file_uploader(
    t("Upload PDF File", "PDF फ़ाइल अपलोड करें"),
    type="pdf"
)

if uploaded_file:

    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    page_number = st.number_input(
        t("Select Page Number", "पेज नंबर चुनें"),
        min_value=1,
        max_value=len(doc),
        value=1
    )

    page = doc[page_number - 1]

    # ----------- LIVE PDF PREVIEW -----------
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")

    st.image(img_bytes, use_column_width=True)

    st.divider()

    # ----------- TEXT ADD SECTION -----------
    st.subheader(t("Add Text to PDF", "PDF में टेक्स्ट जोड़ें"))

    user_text = st.text_area(
        t("Enter Text (Hindi & English Supported)", 
          "टेक्स्ट लिखें (हिंदी और इंग्लिश सपोर्टेड)")
    )

    font_choice = st.selectbox(
        t("Select Font", "फॉन्ट चुनें"),
        ["helv", "cour", "times"]
    )

    font_size = st.slider(
        t("Font Size", "फॉन्ट साइज"),
        8, 72, 16
    )

    x_pos = st.number_input("X", value=50)
    y_pos = st.number_input("Y", value=50)

    if st.button(t("Apply Text", "टेक्स्ट जोड़ें")):

        page.insert_text(
            (x_pos, y_pos),
            user_text,
            fontsize=font_size,
            fontname=font_choice,
            color=(0, 0, 0)
        )

        edited_pdf = BytesIO()
        doc.save(edited_pdf)
        edited_pdf.seek(0)

        st.success(t("Text Added Successfully!", "टेक्स्ट सफलतापूर्वक जोड़ दिया गया!"))

        st.download_button(
            label=t("Download Edited PDF", "एडिट की गई PDF डाउनलोड करें"),
            data=edited_pdf,
            file_name="NJ_Edited.pdf",
            mime="application/pdf"
        )

else:
    st.info(t("Upload a PDF to start editing.", 
              "एडिट करने के लिए PDF अपलोड करें।"))
