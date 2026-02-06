import streamlit as st
import os
import io

# Import Logic Modules
# Ensure these files exist in 'src' folder
from src.pdf_logic import PDFHandler
from src.ocr_logic import extract_text_from_file
from src.word_logic import process_word_file

# ================= PAGE CONFIG =================
st.set_page_config(page_title="NJ All-in-One Editor", layout="wide", page_icon="📝")

# Custom CSS for better look
st.markdown("""
    <style>
    .stButton>button {width: 100%; border-radius: 8px; height: 3em; font-weight: bold;}
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU =================
st.sidebar.title("🛠️ NJ Toolkit")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Select Tool:", 
    [
        "📄 PDF Editor (Live Preview)", 
        "📝 Word Editor (.docx)", 
        "👁️ OCR Scanner (Img to Text)",
        "📂 Saved Files / History"
    ]
)
st.sidebar.info("Tip: Hindi editing ke liye 'Custom Font' option use karein.")

# ================= 1. PDF EDITOR (LIVE PREVIEW) =================
if app_mode == "📄 PDF Editor (Live Preview)":
    st.title("📄 Smart PDF Replacer (Live View)")
    st.markdown("Upload PDF, edit text, and see changes **instantly**.")

    uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

    if uploaded_file:
        # --- SESSION STATE SETUP (Magic Logic) ---
        # Ye check karega ki file nayi hai ya wahi hai jisme edit chal raha hai
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if "current_file_key" not in st.session_state or st.session_state.current_file_key != file_key:
            # New File Load: Reset everything
            st.session_state.current_file_key = file_key
            st.session_state.pdf_bytes = uploaded_file.getvalue()
            st.session_state.edit_counter = 0 

        # Load PDF from Memory (RAM) not directly from upload
        pdf_tool = PDFHandler(io.BytesIO(st.session_state.pdf_bytes))
        
        # --- VIEW SECTION ---
        st.markdown(f"### 👀 Live Preview (Edits Applied: {st.session_state.edit_counter})")
        
        col_pg, col_info = st.columns([1, 3])
        with col_pg:
            total_pages = pdf_tool.get_page_count()
            if total_pages > 0:
                page_num = st.number_input("Page No:", min_value=0, max_value=total_pages-1, value=0)
            else:
                page_num = 0
                
        with col_info:
            st.info(f"Total Pages: {total_pages} | Encrypted: {pdf_tool.is_encrypted}")

        # Show Page Image
        if total_pages > 0:
            st.image(pdf_tool.get_page_image(page_num), caption=f"Page {page_num+1} View", use_container_width=True)
            
            with st.expander("🔍 Show Page Text (For Copying)"):
                st.text_area("Raw Text:", pdf_tool.get_raw_text(page_num), height=100)
        
        st.divider()

        # --- EDIT SECTION ---
        st.markdown("### ✏️ Make Changes")
        
        c1, c2 = st.columns(2)
        with c1:
            old_txt = st.text_input("Find Text (Old):", placeholder="Enter exact text to replace")
        with c2:
            new_txt = st.text_input("Replace With (New):", placeholder="Enter new text here")

        # Font & Alignment Settings
        with st.expander("⚙️ Font & Alignment Settings", expanded=True):
            f_col1, f_col2 = st.columns(2)
            
            with f_col1:
                font_choice = st.selectbox("Choose Font:", ["Standard (English)", "Custom (.ttf)"])
                font_path = None
                if font_choice == "Custom (.ttf)":
                    if os.path.exists("assets"):
                        fonts = [f for f in os.listdir("assets") if f.endswith(".ttf")]
                        sel = st.selectbox("Select Font File:", fonts)
                        if sel: font_path = os.path.join("assets", sel)
                    else:
                        st.warning("⚠️ 'assets' folder not found.")
                
                fs = st.slider("Font Size:", 8, 50, 11)
            
            with f_col2:
                # ✅ Alignment Selector Added
                alignment = st.selectbox("Text Alignment:", ["Left", "Center", "Right"])
                st.caption(f"Text will be aligned: **{alignment}** relative to the original text box.")

        # APPLY BUTTON
        if st.button("🚀 Apply Change & Refresh", type="primary"):
            if old_txt:
                # Pass alignment to logic
                success, count = pdf_tool.search_and_replace(page_num, old_txt, new_txt, font_path, fs, align=alignment)
                
                if success:
                    # Update Memory with new PDF
                    st.session_state.pdf_bytes = pdf_tool.save_pdf()
                    st.session_state.edit_counter += 1
                    st.success(f"✅ Replaced {count} times ({alignment} Aligned)! Refreshing...")
                    st.rerun() # Reloads the app to show new image
                else:
                    st.error("❌ Text not found on this page. Try copying text from 'Show Page Text' box.")
            else:
                st.warning("⚠️ Please enter text to find.")

        # --- FINAL DOWNLOAD ---
        st.divider()
        st.markdown("### 💾 Final Download")
        st.download_button(
            label="⬇️ Download Modified PDF",
            data=st.session_state.pdf_bytes,
            file_name=f"edited_{uploaded_file.name}",
            mime="application/pdf"
        )

# ================= 2. WORD EDITOR =================
elif app_mode == "📝 Word Editor (.docx)":
    st.title("📝 Word Document Replacer")
    st.markdown("Automated Find & Replace for MS Word files.")

    word_file = st.file_uploader("Upload Word File", type=["docx"])

    if word_file:
        c1, c2 = st.columns(2)
        with c1: w_search = st.text_input("Find:")
        with c2: w_replace = st.text_input("Replace:")
            
        if st.button("Run Replacement"):
            if w_search:
                new_docx, count = process_word_file(word_file, w_search, w_replace)
                if new_docx and count > 0:
                    st.success(f"✅ Replaced {count} occurrences!")
                    st.download_button("⬇️ Download Docx", new_docx, "edited_doc.docx", 
                                     mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                else:
                    st.warning("⚠️ Text not found or file error.")

# ================= 3. OCR SCANNER =================
elif app_mode == "👁️ OCR Scanner (Img to Text)":
    st.title("👁️ OCR Scanner (Hindi + English)")
    st.markdown("Extract editable text from Images or PDF scans.")

    ocr_file = st.file_uploader("Upload Image/PDF", type=["png", "jpg", "jpeg", "pdf"])

    if ocr_file:
        if st.button("🔍 Scan Text"):
            with st.spinner("Processing OCR..."):
                text, err = extract_text_from_file(ocr_file)
                if not err:
                    st.success("✅ Scan Complete!")
                    st.text_area("Extracted Text:", text, height=300)
                    
                    # ✅ FIX: Saving History with UTF-8 (Hindi Support)
                    try:
                        with open("scanned_history.txt", "a", encoding="utf-8") as f:
                            f.write(f"\n--- New Scan ---\n{text}\n")
                    except Exception as e:
                        st.error(f"Could not save history: {e}")
                    
                    # ✅ FIX: Downloading with UTF-8 BOM/Charset
                    st.download_button(
                        label="⬇️ Download Text File", 
                        data=text, 
                        file_name="scanned_text.txt",
                        mime="text/plain; charset=utf-8"  # Hindi Fix Here
                    )
                else:
                    st.error(f"OCR Error: {err}")

# ================= 4. FILE MANAGER =================
elif app_mode == "📂 Saved Files / History":
    st.title("📂 Server File Manager")
    st.markdown("Files saved on the server (History/Logs).")

    all_files = os.listdir()
    relevant_files = [f for f in all_files if f.endswith(('.txt', '.pdf', '.docx', '.log'))]

    if not relevant_files:
        st.info("No files found.")
    else:
        for file_name in relevant_files:
            col_name, col_btn = st.columns([3, 1])
            with col_name:
                st.write(f"📄 **{file_name}**")
            with col_btn:
                try:
                    with open(file_name, "rb") as f:
                        # Determine Mime Type
                        mime_type = "application/octet-stream"
                        if file_name.endswith(".txt"): mime_type = "text/plain; charset=utf-8"
                        elif file_name.endswith(".pdf"): mime_type = "application/pdf"
                        
                        st.download_button("⬇️ Download", f.read(), file_name, mime=mime_type, key=file_name)
                except Exception as e:
                    st.error("Locked")
            st.divider()
            
