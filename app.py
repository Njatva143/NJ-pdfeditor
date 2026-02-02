import streamlit as st
import os
# Humare custom modules
from src.pdf_logic import PDFHandler
from src.ocr_logic import extract_text_from_image, image_to_pdf

st.set_page_config(page_title="Pro Doc Editor", layout="wide")

st.title("📱 Professional Document Editor")
st.sidebar.title("Tools Menu")

app_mode = st.sidebar.selectbox("Choose Mode", ["PDF Editor", "Scanner (OCR)", "Word Editor"])

# --- MODE 1: PDF EDITOR ---
if app_mode == "PDF Editor":
    st.header("📄 PDF Text Editor")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        pdf_tool = PDFHandler(uploaded_file.read())
        
        # Security Check
        if pdf_tool.is_encrypted:
            st.error("🔒 Locked PDF! Password hatakar upload karein.")
        else:
            total_pages = pdf_tool.get_page_count()
            page_num = st.sidebar.number_input("Page No", 1, total_pages, 1) - 1
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Edit Text")

                # --- 1. FONT SELECTOR (Naya Feature) ---
                available_fonts = ["Default (English Only)"]
                
                # Check agar assets folder hai
                if os.path.exists("assets"):
                    for f in os.listdir("assets"):
                        if f.endswith(".ttf") or f.endswith(".otf"):
                            available_fonts.append(f)
                else:
                    st.warning("⚠️ 'assets' folder nahi mila. Hindi font ke liye folder banayein.")

                selected_font = st.selectbox("Choose Font", available_fonts)
                
                # Font ka path set karna
                font_path = None
                if selected_font != "Default (English Only)":
                    font_path = os.path.join("assets", selected_font)

                # --- 2. RAW TEXT VIEWER ---
                with st.expander("🔍 See Raw Text"):
                    st.text_area("System View:", pdf_tool.get_raw_text(page_num), height=100)

                # --- 3. EDIT INPUTS ---
                old_txt = st.text_input("Find Text")
                new_txt = st.text_input("Replace With")
                
                if st.button("Apply Changes"):
                    success, count = pdf_tool.search_and_replace(page_num, old_txt, new_txt, font_path)
                    if success:
                        st.success(f"Success! {count} changes made using {selected_font}.")
                    else:
                        st.error("Text not found.")

            with col2:
                st.subheader("Preview")
                st.image(pdf_tool.get_page_image(page_num), use_column_width=True)

            st.download_button("Download PDF", pdf_tool.save_pdf(), "edited_doc.pdf")

# --- MODE 2: SCANNER (OCR) ---
elif app_mode == "Scanner (OCR)":
    st.header("📷 Image Scanner & OCR")
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, width=300)
        if st.button("Extract Text"):
            text = extract_text_from_image(uploaded_image.getvalue())
            st.text_area("Result", text)
        if st.button("Convert to PDF"):
            pdf_data = image_to_pdf(uploaded_image.getvalue())
            if pdf_data: st.download_button("Download PDF", pdf_data, "scan.pdf")

# --- MODE 3: WORD EDITOR ---
elif app_mode == "Word Editor":
    st.info("🚧 Coming Soon...")
    
