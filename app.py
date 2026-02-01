import streamlit as st
from src.pdf_logic import PDFHandler

st.set_page_config(page_title="Pro Doc Editor", layout="wide")

st.title("📱 Professional Document Editor")
st.sidebar.title("Tools Menu")

app_mode = st.sidebar.selectbox("Choose Mode", ["PDF Editor", "Word Editor", "Scanner (OCR)"])

if app_mode == "PDF Editor":
    st.header("📄 PDF Magic Tool")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        # हमारे src/pdf_logic.py का इस्तेमाल
        pdf_tool = PDFHandler(uploaded_file.read())
        
        # साइडबार में पेज नेविगेशन
        total_pages = pdf_tool.get_page_count()
        page_num = st.sidebar.number_input("Page No", 1, total_pages, 1) - 1
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Edit Text")
            old_txt = st.text_input("Find Text")
            new_txt = st.text_input("Replace With")
            
            if st.button("Update PDF"):
                success, count = pdf_tool.search_and_replace(page_num, old_txt, new_txt)
                if success:
                    st.success(f"Changed {count} locations!")
                else:
                    st.warning("Text not found.")

        with col2:
            st.subheader("Preview")
            img_data = pdf_tool.get_page_image(page_num)
            st.image(img_data, use_column_width=True)

        # डाउनलोड बटन
        st.markdown("---")
        st.download_button("Download New PDF", pdf_tool.save_pdf(), "edited.pdf")

elif app_mode == "Word Editor":
    st.info("Word editing module is under construction in src/word_logic.py")

elif app_mode == "Scanner (OCR)":
    st.info("OCR module coming soon in src/ocr_logic.py")
  
