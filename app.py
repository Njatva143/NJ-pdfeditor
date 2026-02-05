import streamlit as st
import os

# Import Logic Modules
from src.pdf_logic import PDFHandler
from src.ocr_logic import extract_text_from_file
from src.word_logic import process_word_file

# ================= PAGE CONFIG =================
st.set_page_config(page_title="NJ All-in-One Editor", layout="wide", page_icon="📝")

# CSS for styling
st.markdown("""
    <style>
    .stButton>button {width: 100%; border-radius: 5px; height: 3em;}
    .reportview-container {background: #f0f2f6;}
    h1 {color: #2e86de;}
    </style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU =================
st.sidebar.title("🛠️ NJ Toolkit")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Select Tool:", 
    ["📄 PDF Editor (Hindi Support)", "📝 Word Editor (.docx)", "👁️ OCR Scanner (Img to Text)"]
)
st.sidebar.markdown("---")
st.sidebar.info("Tip: Hindi font ke liye 'Unicode' font use karein.")

# ================= 1. PDF EDITOR =================
if app_mode == "📄 PDF Editor (Hindi Support)":
    st.title("📄 Smart PDF Replacer (With Hindi Sticker)")
    
    uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

    if uploaded_file:
        pdf_tool = PDFHandler(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Total Pages: {pdf_tool.get_page_count()}")
        with col2:
            if pdf_tool.is_encrypted:
                st.error("⚠️ PDF is Password Protected!")

        # --- Settings ---
        with st.expander("⚙️ Font Settings (For Hindi Fix)", expanded=True):
            font_choice = st.selectbox("Choose Font:", ["Standard (English)", "Custom Font (.ttf)"])
            
            font_path = None
            if font_choice == "Custom Font (.ttf)":
                # Assets folder se font uthayein
                font_files = [f for f in os.listdir("assets") if f.endswith(".ttf")] if os.path.exists("assets") else []
                selected_font = st.selectbox("Select Font File:", font_files)
                if selected_font:
                    font_path = os.path.join("assets", selected_font)
            
            user_font_size = st.slider("Font Size:", 8, 30, 11)

        # --- Edit Section ---
        c1, c2 = st.columns(2)
        with c1:
            old_txt = st.text_input("Find Text (Old):")
        with c2:
            new_txt = st.text_input("Replace With (New):")
            
        page_num = st.number_input("Page Number (0 for Page 1):", min_value=0, max_value=pdf_tool.get_page_count()-1, value=0)

        if st.button("🚀 Replace Text"):
            if not old_txt:
                st.warning("Please enter text to find.")
            else:
                success, count = pdf_tool.search_and_replace(
                    page_num, old_txt, new_txt, font_path, user_font_size
                )
                
                if success:
                    st.success(f"✅ Changed {count} locations!")
                    
                    # Preview Image
                    st.image(pdf_tool.get_page_image(page_num), caption="Preview (After Edit)", use_container_width=True)
                    
                    # Download
                    pdf_data = pdf_tool.save_pdf()
                    st.download_button("💾 Download Edited PDF", pdf_data, "edited_file.pdf", "application/pdf")
                else:
                    st.error("❌ Text not found on this page.")

# ================= 2. WORD EDITOR =================
elif app_mode == "📝 Word Editor (.docx)":
    st.title("📝 Word Document Replacer")
    st.markdown("Upload a `.docx` file to find and replace text automatically.")

    word_file = st.file_uploader("Upload Word File", type=["docx"])

    if word_file:
        c1, c2 = st.columns(2)
        with c1:
            w_search = st.text_input("Find Text:")
        with c2:
            w_replace = st.text_input("Replace With:")
            
        if st.button("Run Replacement"):
            if w_search:
                new_docx_bytes, count = process_word_file(word_file, w_search, w_replace)
                
                if new_docx_bytes:
                    if count == 0:
                        st.warning("⚠️ Text not found anywhere in the document.")
                    else:
                        st.success(f"✅ Replaced {count} occurrences!")
                        st.download_button(
                            label="💾 Download New Word File",
                            data=new_docx_bytes,
                            file_name="edited_doc.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error(f"Error processing file: {count}") # count holds error msg here
            else:
                st.warning("Please enter search text.")

# ================= 3. OCR SCANNER =================
elif app_mode == "👁️ OCR Scanner (Img to Text)":
    st.title("👁️ OCR Scanner (Hindi + English)")
    st.markdown("Upload Image or Scanned PDF to extract editable text.")

    ocr_file = st.file_uploader("Upload File", type=["png", "jpg", "jpeg", "pdf"])

    if ocr_file:
        if st.button("🔍 Extract Text"):
            with st.spinner("Scanning..."):
                extracted_text, error = extract_text_from_file(ocr_file)
                
                if error:
                    st.error(f"OCR Failed: {error}")
                else:
                    st.success("Scan Complete!")
                    st.text_area("Copy your text:", extracted_text, height=300)
                    st.download_button("💾 Save as Text File", extracted_text, "scanned.txt")
                    
