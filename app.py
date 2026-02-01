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
        # src/pdf_logic.py से क्लास को कॉल करना
        pdf_tool = PDFHandler(uploaded_file.read())
        
        # पेज नेविगेशन
        total_pages = pdf_tool.get_page_count()
        page_num = st.sidebar.number_input("Page No", 1, total_pages, 1) - 1
        
        col1, col2 = st.columns([1, 1])
        
        # --- संपादन (Editing) सेक्शन ---
        with col1:
            st.subheader("Edit Text")
            
            # 👇👇👇 नया कोड यहाँ जोड़ा गया है 👇👇👇
            with st.expander("🔍 See Raw Text (Copy from here)"):
                try:
                    # यह फंक्शन src/pdf_logic.py में होना चाहिए
                    raw_text = pdf_tool.get_raw_text(page_num) 
                    st.text_area("PDF Text:", raw_text, height=150)
                    st.info("ऊपर वाले बॉक्स से टेक्स्ट कॉपी करें और नीचे 'Find Text' में पेस्ट करें।")
                except AttributeError:
                    st.error("Error: आपने src/pdf_logic.py फाइल अपडेट नहीं की है! कृपया पिछला कोड देखें।")
            # 👆👆👆 नया कोड यहाँ खत्म हुआ 👆👆👆

            old_txt = st.text_input("Find Text (Paste Exact Text)")
            new_txt = st.text_input("Replace With")
            
            if st.button("Update PDF"):
                # सर्च और रिप्लेस करना
                success, count = pdf_tool.search_and_replace(page_num, old_txt, new_txt)
                if success:
                    st.success(f"Success! {count} जगहों पर बदलाव किया गया।")
                else:
                    st.warning("Text not found. (ऊपर वाले 'Raw Text' बॉक्स को चेक करें)")

        # --- प्रिव्यू (Preview) सेक्शन ---
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
