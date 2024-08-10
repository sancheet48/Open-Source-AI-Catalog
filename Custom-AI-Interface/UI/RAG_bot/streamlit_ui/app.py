
import os
import sys
import logging
import requests
import json
import const
import streamlit as st
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from logging.handlers import RotatingFileHandler


__version__ = "0.1.0"

logger = logging.getLogger(__file__)


def startup():
    """Startup method to check for environment variables."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - %(levelname)s: %(message)s",
        handlers=[
            RotatingFileHandler(
                const.LOG_FILE,
                maxBytes=5 * 1024 * 1024,
                backupCount=9,
                encoding="utf8",
            ),
            logging.StreamHandler(),
        ],
    )

    missing = []
    if not const.BACKEND_APP_URI:
        missing.append("BACKEND_APP_URI")
    if missing:
        logging.error(
            "Environment variables: %s not defined. Exiting Application",
            ", ".join(missing),
        )
        sys.exit(-1)
    logger.info("Deleting Proxies from the Env")
    for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if key in os.environ:
            del os.environ[key]

# extracting text from pdf
def get_pdf_text(docs):
    text = ""
    for pdf in docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# converting text to chunks
def get_chunks(raw_text):
    text_splitter =  RecursiveCharacterTextSplitter(
                                        chunk_size=1000,
                                        chunk_overlap=200,
                                        )
    chunks = text_splitter.split_text(raw_text)
    return chunks



def get_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2",
                                    model_kwargs={'device': 'cpu'})
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore




def call_api(question):

    url = const.BACKEND_APP_URI # "http://127.0.0.1:8000/query/"
    data = {
        "question": question,
        "input_prompt": "You are a helpful assistant to answer the given question from the user.",
        "temperature": 0.2,
        "messages": [
            {
                "User": "",
                "Assistant": ""
            }
        ],
        "repetition_penalty": 1.1,
        "top_k": 40,
        "top_p": 0.95,
        "context_length": 2048
    }


    headers = {
        "Content-Type": "application/json"
    }


    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return response.json()["response"]
    return "API call failed"


def main():
    startup()

    with st.sidebar:
        st.subheader("Your documents")
        docs = st.file_uploader("Upload your PDF here and click on 'Process'", accept_multiple_files=True)
        
        
        process_button_disabled = not docs
        if docs and st.button("Process", disabled=process_button_disabled):
            with st.spinner("Processing"):
                # get the pdf
                raw_text = get_pdf_text(docs)

                # get the text chunks
                text_chunks = get_chunks(raw_text)

                # create vectorstore
                vectorstore = get_vectorstore(text_chunks)

                # Store vectorstore in session state
                st.session_state.vectorstore = vectorstore



    st.title("RAG Bot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    response = "Please create the embeddings first by uploading the documents."
    if input_prompt := st.chat_input("What is up?"):

        st.chat_message("user").markdown(input_prompt)

        st.session_state.messages.append({"role": "user", "content": input_prompt})
        if 'vectorstore' in st.session_state and input_prompt:
            vectorstore = st.session_state.vectorstore
            relevant_docs = vectorstore.similarity_search(input_prompt)
            combined_input = (
                "Here are some documents that might help answer the question: "
                + input_prompt
                + "\n\nRelevant Documents:\n"
                + "\n\n".join([doc.page_content for doc in relevant_docs])
                + "\n\nPlease provide an answer based only on the provided documents. If the answer is not found in the documents, respond with 'I'm not sure'."
            )
            
            response = call_api(combined_input)
            
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    main()
