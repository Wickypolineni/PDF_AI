import os
import PyPDF2
import streamlit as st
from io import StringIO
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import CallbackManager
def get_openai_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return openai_api_key
    else:
        # Replace "your_api_key" with your actual OpenAI API key
        return "your_api_key"
st.set_page_config(page_title="PDF AI")
@st.cache_data
def load_docs(files):
    st.info("`Reading doc ...`")
    all_text = ""
    pdf_pages = []
    for file_path in files:
        file_extension = os.path.splitext(file_path.name)[1]
        if file_extension == ".pdf":
            pdf_reader = PyPDF2.PdfReader(file_path)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text += page.extract_text()
            all_text += text
            pdf_pages.append((file_path.name, str(page_num + 1)))  # Convert page_num to a string
        elif file_extension == ".txt":
            stringio = StringIO(file_path.getvalue().decode("utf-8"))
            text = stringio.read()
            all_text += text
        else:
            st.warning('Please provide txt or pdf.', icon="⚠️")
    return all_text, pdf_pages
@st.cache_resource
def create_retriever(_embeddings, splits):
    try:
        vectorstore = FAISS.from_texts(splits, _embeddings)
    except (IndexError, ValueError) as e:
        st.error(f"Error creating vectorstore: {e}")
        return
    retriever = vectorstore.as_retriever(k=5)
    return retriever
@st.cache_resource
def split_texts(text, chunk_size, overlap, split_method):
    st.info("`Splitting doc ...`")
    split_method = "RecursiveTextSplitter"
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap)
    splits = text_splitter.split_text(text)
    if not splits:
        st.error("Failed to split document")
        st.stop()
    return splits
def main():
    st.markdown(
        """
        <style>
            footer {visibility: hidden;}
            .css-card {
                border-radius: 0px;
                padding: 30px 10px 10px 10px;
                background-color: #f8f9fa;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 10px;
                font-family: "IBM Plex Sans", sans-serif;
            }
            .card-tag {
                border-radius: 0px;
                padding: 1px 5px 1px 5px;
                margin-bottom: 10px;
                position: absolute;
                left: 0px;
                top: 0px;
                font-size: 0.6rem;
                font-family: "IBM Plex Sans", sans-serif;
                color: white;
                background-color: green;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.write(
    f"""
    <div style="display: flex; align-items: center; margin-left: 0;">
        <h1 style="display: inline-block;">PDF AI</h1>
        <sup style="margin-left:5px;font-size:small; color: green;">beta</sup>
    </div>
    """,
    unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader("Upload a PDF or TXT Document", type=[
                                      "pdf", "txt"], accept_multiple_files=True)
    if uploaded_files:
        loaded_text, pdf_pages = load_docs(uploaded_files)
        st.write("Documents uploaded and processed.")
        splits = split_texts(loaded_text, chunk_size=1000, overlap=0, split_method="RecursiveCharacterTextSplitter")
        num_chunks = len(splits)
        st.write(f"Number of text chunks: {num_chunks}")
        openai_api_key = get_openai_api_key()
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        retriever = create_retriever(embeddings, splits)
        callback_handler = StreamingStdOutCallbackHandler()
        callback_manager = CallbackManager([callback_handler])
        chat_openai = ChatOpenAI(streaming=True, callback_manager=callback_manager, verbose=True, temperature=0, openai_api_key=openai_api_key)
        qa = RetrievalQA.from_chain_type(llm=chat_openai, retriever=retriever, chain_type="stuff", verbose=True)
        st.write("Ready to answer questions.")
        user_question = st.text_input("Enter your question:")
        if user_question:
            answer = qa.run(user_question)
            st.write("Answer:", answer)
            if pdf_pages:
                matching_pages = [f"Page {page} from {pdf_name}" for pdf_name, page in pdf_pages if str(page) in answer]
                if matching_pages:
                    st.write("Retrieved from:", ", ".join(matching_pages))
                else:
                    st.write("Page information not found for the answer.")
            else:
                st.write("No PDF pages information available.")
            pdf_names = [pdf_name for pdf_name, _ in pdf_pages]
            if len(set(pdf_names)) > 1:
                st.write(f"Answer comes from multiple PDFs: {', '.join(set(pdf_names))}")
if __name__ == "__main__":
    main()
