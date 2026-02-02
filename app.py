import streamlit as st
import os
# हमारे लॉजिक फाइल्स
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
            st.error("🔒 यह PDF लॉक है! कृपया पासवर्ड हटाकर अपलोड करें।")
        else:
            # पेज नेविगेशन
            total_pages = pdf_tool.get_page_count()
            page_num = st.sidebar.number_input("Page No", 1, total_pages, 1) - 1
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Edit Options")

                # 1. Font Selector (assets फोल्डर से)
                available_fonts = ["Default (English)"]
                if os.path.exists("assets"):
                    for f in os.listdir("assets"):
                        if f.endswith(".ttf") or f.endswith(".otf"):
                            available_fonts.append(f)
                else:
                    st.warning("⚠️ 'assets' फोल्डर नहीं मिला। हिंदी फॉन्ट के लिए फोल्डर बनाएं।")

                selected_font = st.selectbox("Choose Font", available_fonts)
                
                font_path = None
                if selected_font != "Default (English)":
                    font_path = os.path.join("assets", selected_font)

                # 2. Raw Text Viewer
                with st.expander("🔍 See Raw Text (Copy text from here)"):
                    st.text_area("System View:", pdf_tool.get_raw_text(page_num), height=100)

                # 3. Text Inputs & Size Slider
                old_txt = st.text_input("Find Text (Paste Exact Text)")
                new_txt = st.text_input("Replace With")
                
                # 👇 साइज़ स्लाइडर (डिफ़ॉल्ट 11 है, हिंदी के लिए 20-25 करें)
                user_font_size = st.slider("Adjust Font Size", 5, 50, 11)
                
                if st.button("Apply Changes"):
                    # फंक्शन को साइज़ भेज रहे हैं
                    success, count = pdf_tool.search_and_replace(
                        page_num, old_txt, new_txt, font_path, user_font_size
                    )
                    
                    if success:
                        st.success(f"Success! {count} जगहों पर बदलाव हुआ (Size: {user_font_size})")
                    else:
                        st.error("Text not found. (Raw Text बॉक्स चेक करें)")

            with col2:
                st.subheader("Preview")
                st.image(pdf_tool.get_page_image(page_num), use_column_width=True)

            st.markdown("---")
            st.download_button("Download Final PDF", pdf_tool.save_pdf(), "edited_doc.pdf")

# --- MODE 2: SCANNER (OCR) ---
elif app_mode == "Scanner (OCR)":
    st.header("📷 Image Scanner & OCR")
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, width=300)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Extract Text"):
                text = extract_text_from_image(uploaded_image.getvalue())
                st.text_area("Result", text, height=200)
        with col2:
            if st.button("Convert to PDF"):
                pdf_data = image_to_pdf(uploaded_image.getvalue())
                if pdf_data:
                    st.download_button("Download PDF", pdf_data, "scan.pdf")

# --- MODE 3: WORD EDITOR ---
elif app_mode == "Word Editor":
    st.info("🚧 Word (.docx) Editor coming soon...")
    
