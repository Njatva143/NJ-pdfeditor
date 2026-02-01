import streamlit as st
from src.pdf_logic import PDFHandler
from src.ocr_logic import extract_text_from_image, image_to_pdf

st.set_page_config(page_title="Pro Doc Editor", layout="wide")

st.title("📱 Professional Document Editor")
st.sidebar.title("Tools Menu")

app_mode = st.sidebar.selectbox("Choose Mode", ["PDF Editor", "Scanner (OCR)", "Word Editor"])

if app_mode == "PDF Editor":
    st.header("📄 PDF Text Editor")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        # PDF लोड करें
        pdf_tool = PDFHandler(uploaded_file.read())
        
        # --- SECURITY CHECK (नया फीचर) ---
        if pdf_tool.is_encrypted:
            st.error("🔒 यह PDF Password Protected है! कृपया पहले इसका पासवर्ड हटाएं या कोई और PDF अपलोड करें।")
        else:
            # अगर PDF लॉक नहीं है, तभी आगे बढ़ें
            total_pages = pdf_tool.get_page_count()
            page_num = st.sidebar.number_input("Page No", 1, total_pages, 1) - 1
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Edit Text")
                
                # Raw Text Viewer
                with st.expander("🔍 See Raw Text (Copy for accuracy)"):
                    try:
                        raw_text = pdf_tool.get_raw_text(page_num)
                        st.text_area("System Text View:", raw_text, height=100)
                        if not raw_text.strip():
                            st.warning("⚠️ यह बॉक्स खाली है? इसका मतलब यह Scanned PDF (फोटो) है। कृपया 'Scanner (OCR)' मोड यूज़ करें।")
                    except Exception as e:
                        st.error(f"Error reading text: {e}")

                old_txt = st.text_input("Find Text (Paste Exact Text)")
                new_txt = st.text_input("Replace With")
                
                if st.button("Apply Changes"):
                    success, count = pdf_tool.search_and_replace(page_num, old_txt, new_txt)
                    if success:
                        st.success(f"Success! {count} जगह बदलाव हो गया।")
                    else:
                        st.error("Text Not Found. (शायद स्पेलिंग मैच नहीं हो रही)")

            with col2:
                st.subheader("Live Preview")
                try:
                    img_data = pdf_tool.get_page_image(page_num)
                    st.image(img_data, use_column_width=True)
                except Exception as e:
                    st.error("Preview load नहीं हो पाया।")

            st.markdown("---")
            st.download_button("Download Edited PDF", pdf_tool.save_pdf(), "final_document.pdf")

elif app_mode == "Scanner (OCR)":
    st.header("📷 Image Scanner & OCR")
    uploaded_image = st.file_uploader("Upload Image (JPG/PNG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", width=300)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Extract Text (OCR)"):
                with st.spinner("Reading text..."):
                    text = extract_text_from_image(uploaded_image.getvalue())
                    st.text_area("Extracted Result:", text, height=200)
        with col2:
            if st.button("Convert to PDF"):
                pdf_data = image_to_pdf(uploaded_image.getvalue())
                if pdf_data:
                    st.download_button("Download PDF", pdf_data, "scanned.pdf", "application/pdf")

elif app_mode == "Word Editor":
    st.info("🚧 Word (.docx) Editor is under construction.")
    
