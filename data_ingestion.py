from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_and_chunk(file_path):
    """Loads a PDF and splits it into smaller chunks for the Vector DB."""
    # 1. Load the document
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # 2. Chunk the text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    
    return splits