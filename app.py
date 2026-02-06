import streamlit as st
import os

# Import Logic Modules
from src.pdf_logic import PDFHandler
from src.ocr_logic import extract_text_from_file
from src.word_logic import process_word_file

# ================= PAGE CONFIG =================
st.set_page_config(page_title="NJ All-in-One Editor", layout="wide", page_icon="📝")

st.markdown("""
    <style>
    .stButton>button {width: 100%; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU =================
st.sidebar.title("🛠️ NJ Toolkit")
st.sidebar.markdown("---")

# ✅ New Option Added: "📂 Saved Files / History"
app_mode = st.sidebar.radio(
    "Select Tool:", 
    [
        "📄 PDF Editor (Hindi Support)", 
        "📝 Word Editor (.docx)", 
        "👁️ OCR Scanner (Img to Text)",
        "📂 Saved Files / History"  # <--- NEW BUTTON
    ]
)
st.sidebar.markdown("---")

# ================= 1. PDF EDITOR =================
if app_mode == "📄 PDF Editor (Hindi Support)":
    st.title("📄 Smart PDF Replacer")
    uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

    if uploaded_file:
        pdf_tool = PDFHandler(uploaded_file)
        
        # Preview Section
        st.markdown("### 👀 Page Preview")
        col_pg, col_info = st.columns([1, 3])
        with col_pg:
            page_num = st.number_input("Page No:", min_value=0, max_value=pdf_tool.get_page_count()-1, value=0)
        with col_info:
            st.info(f"Total Pages: {pdf_tool.get_page_count()}")
        
        st.image(pdf_tool.get_page_image(page_num), caption=f"Page {page_num+1}", use_container_width=True)
        
        with st.expander("🔍 Show Page Text"):
            st.text_area("Raw Text:", pdf_tool.get_raw_text(page_num), height=100)

        st.markdown("---")
        st.markdown("### ✏️ Find & Replace")
        
        c1, c2 = st.columns(2)
        with c1:
            old_txt = st.text_input("Find Text:", placeholder="Old Text")
        with c2:
            new_txt = st.text_input("Replace With:", placeholder="New Text")

        with st.expander("⚙️ Font Settings"):
            font_choice = st.selectbox("Choose Font:", ["Standard", "Custom (.ttf)"])
            font_path = None
            if font_choice == "Custom (.ttf)":
                if os.path.exists("assets"):
                    fonts = [f for f in os.listdir("assets") if f.endswith(".ttf")]
                    sel = st.selectbox("Select Font:", fonts)
                    if sel: font_path = os.path.join("assets", sel)
            fs = st.slider("Size:", 8, 40, 11)

        if st.button("🚀 Replace & Download"):
            if old_txt:
                success, count = pdf_tool.search_and_replace(page_num, old_txt, new_txt, font_path, fs)
                if success:
                    st.success(f"Replaced {count} times!")
                    pdf_data = pdf_tool.save_pdf()
                    st.download_button("⬇️ Download PDF", pdf_data, "edited_output.pdf", "application/pdf")
                else:
                    st.error("Text not found.")

# ================= 2. WORD EDITOR =================
elif app_mode == "📝 Word Editor (.docx)":
    st.title("📝 Word Document Replacer")
    word_file = st.file_uploader("Upload Word File", type=["docx"])

    if word_file:
        c1, c2 = st.columns(2)
        with c1: w_search = st.text_input("Find:")
        with c2: w_replace = st.text_input("Replace:")
            
        if st.button("Run Replacement"):
            if w_search:
                new_docx, count = process_word_file(word_file, w_search, w_replace)
                if new_docx and count > 0:
                    st.success(f"Replaced {count} times!")
                    st.download_button("⬇️ Download Docx", new_docx, "edited_doc.docx")
                else:
                    st.warning("Text not found.")

# ================= 3. OCR SCANNER =================
elif app_mode == "👁️ OCR Scanner (Img to Text)":
    st.title("👁️ OCR Scanner")
    ocr_file = st.file_uploader("Upload Image/PDF", type=["png", "jpg", "pdf"])

    if ocr_file:
        if st.button("🔍 Scan Text"):
            with st.spinner("Scanning..."):
                text, err = extract_text_from_file(ocr_file)
                if not err:
                    st.success("Done!")
                    st.text_area("Result:", text, height=300)
                    
                    # ✅ Save to file automatically for history
                    with open("scanned_history.txt", "a") as f:
                        f.write(f"\n--- New Scan ---\n{text}\n")
                    
                    st.download_button("⬇️ Download Text", text, "scan.txt")
                else:
                    st.error(err)

# ================= 4. FILE MANAGER (NEW) =================
elif app_mode == "📂 Saved Files / History":
    st.title("📂 File Manager")
    st.markdown("View and download files present in your server directory.")

    # Current folder me saari files dhoondo
    all_files = os.listdir()
    
    # Filter only relevant files (.txt, .pdf, .docx)
    relevant_files = [f for f in all_files if f.endswith(('.txt', '.pdf', '.docx', '.log'))]

    if not relevant_files:
        st.info("No saved files found yet.")
    else:
        st.write(f"Found {len(relevant_files)} files:")
        
        # Ek Table jaisa banayenge
        for file_name in relevant_files:
            col_name, col_btn = st.columns([3, 1])
            
            with col_name:
                st.text(f"📄 {file_name}")
            
            with col_btn:
                # File ko read karke download button banao
                with open(file_name, "rb") as f:
                    file_data = f.read()
                    st.download_button(
                        label="⬇️ Download",
                        data=file_data,
                        file_name=file_name,
                        key=file_name # Unique key zaroori hai
                    )
            st.divider()
            
