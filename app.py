import streamlit as st
import os
import time
from data_ingestion import extract_and_chunk
from vector_engine import create_vector_db
#from llm_generator import get_rag_chain

# --- Page Configuration ---
st.set_page_config(page_title="RAGMentor", layout="wide", page_icon="📘")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "file_name" not in st.session_state:
    st.session_state.file_name = ""
if "last_time" not in st.session_state:
    st.session_state.last_time = 0.0
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

# --- Sidebar Layout (Clean Navigation) ---
with st.sidebar:
    st.title("📘 RAGMentor")
    st.caption("Learn Smarter with Your Documents")
    
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.vectorstore = None
        st.session_state.file_name = ""
        st.rerun()
        
    st.divider()
    st.markdown("### Navigation")
    st.caption("📂 My Documents")
    st.caption("💬 Chat History")
    st.caption("📄 Document Summary")
    st.caption("⚙️ Settings")
    
    st.divider()
    st.subheader("Recent Chats")
    st.caption("Capital of France?")
    st.caption("Key findings of the paper")
    st.caption("Explain methodology")

# --- Main Interface Layout ---
col1, col2 = st.columns([2.5, 1])

with col1:
    st.header("💬 Chat with your Documents")
    
    # --- CHATGPT STYLE DOCUMENT UPLOAD BOX (Right above/near chat input) ---
    uploaded_file = st.file_uploader("📎 Upload your PDF document to chat", type=["pdf"], key="chat_upload")
    
    if uploaded_file and st.session_state.vectorstore is None:
        with st.spinner("Processing document... Extracting and chunking..."):
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Call team modules (Lalitha & Rahul's code)
            splits = extract_and_chunk(temp_path)
            st.session_state.vectorstore = create_vector_db(splits)
            st.session_state.file_name = uploaded_file.name
            
            os.remove(temp_path)
            st.success(f"Successfully loaded: {uploaded_file.name}")
    elif uploaded_file is not None:
        st.info(f"📁 Active Document: {st.session_state.file_name}")

    st.divider()

    # Render Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat Input Box
    user_query = st.chat_input("Ask a question about your documents...")
    
    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.chat_message("assistant"):
            if st.session_state.vectorstore is None:
                st.error("Please upload a PDF document first using the uploader above!")
            else:
                with st.spinner("Searching document..."):
                    start_time = time.time()
                    
                    # Generate Answer using RAG Chain (Kavya's code)
                    #rag_chain = get_rag_chain(st.session_state.vectorstore)
                    #response = rag_chain.invoke({"input": user_query})
                    #answer = response["answer"]
                    
                    # Save metrics for dashboard
                    st.session_state.last_time = round(time.time() - start_time, 2)
                    st.session_state.last_answer = answer
                    
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

with col2:
    # Right Panel Dashboard (Metrics UI)
    st.markdown("""
        <style>
        .metrics-box { 
            background-color: #1e2530; 
            padding: 15px; 
            border-radius: 10px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='metrics-box'>", unsafe_allow_html=True)
    st.subheader("📊 Metrics")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Documents", "1" if st.session_state.vectorstore else "0")
    with col_m2:
        st.metric("Chats", len(st.session_state.chat_history)//2)
        
    st.divider()
    st.subheader("📈 RAG Performance")
    
    time_taken = st.session_state.last_time
    st.metric("Retrieved Chunks", "3" if st.session_state.vectorstore else "0")
    st.metric("Response Time", f"{time_taken} s")
    
    st.markdown("</div>", unsafe_allow_html=True)
