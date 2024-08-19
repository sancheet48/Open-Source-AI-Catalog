import os
import sys
import logging
import streamlit as st
from streamlit_option_menu import option_menu
from logging.handlers import RotatingFileHandler
import const
from langchain_community.llms import CTransformers




__version__ = "0.1.0"

logger = logging.getLogger(__file__)


containers = [
        {
            "title": "General Purpose Chatbot",
            "description": "",
            "tags": "Generic chatbot api.",
            "url": const.GENERIC_CHATBOT_URI,
        },
        {
            "title": "Retrieval Augmented Generation  Chatbot",
            "description": "",
            "tags": "Chat with your own custom data.",
            "url": const.RAG_CHATBOT_URI,
        },
        {
            "title": "SQL  Chatbot",
            "description": "",
            "tags": "Chat with your own SQL database.",
            "url": const.SQL_CHATBOT_URI,
        },
        {
            "title": "MongoDb  Chatbot",
            "description": "",
            "tags": "Chat with own MongoDb(NoSQL) database.",
            "url": const.MONGO_DB_CHATBOT_URI,
        },
    ]

models = [
        {
            "title": "Mistral-7B-Instruct-v0.3",
            "description": "Mistral AI is a French company specializing in artificial intelligence products. Founded in April 2023 by former employees of Meta Platforms and Google DeepMind, the company has quickly risen to prominence in the AI sector.",

            "url": const.MISTRAL_URI,
        },
        {
            "title": "Meta-Llama-3.1-8B-Instruct",
            "description": "The Meta Llama 3.1 collection of multilingual large language models (LLMs) is a collection of pretrained and instruction tuned generative models in 8B, 70B and 405B sizes (text in/text out).",

            "url": const.LLAMA_URI,
        },
        {
            "title": "Google Gemma-2-9b-it",
            "description": "Gemma is a family of lightweight, state-of-the-art open models from Google, built from the same research and technology used to create the Gemini models.",

            "url": const.GEMMA_URI,
        },
    ]


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
    if not const.GENERIC_CHATBOT_URI:
        missing.append("GENERIC_CHATBOT_URI")
    if not const.RAG_CHATBOT_URI:
        missing.append("RAG_CHATBOT_URI")

    if not const.SQL_CHATBOT_URI:
        missing.append("SQL_CHATBOT_URI")
    if not const.MONGO_DB_CHATBOT_URI:
        missing.append("MONGO_DB_CHATBOT_URI")

    if not const.MISTRAL_URI:
        missing.append("MISTRAL_URI")
    if not const.LLAMA_URI:
        missing.append("LLAMA_URI")
    if not const.GEMMA_URI:
        missing.append("GEMMA_URI")

        
    if missing:
        logging.error(
            "Environment variables: %s not defined. Exiting Application",
            ", ".join(missing),
        )
        sys.exit(-1)



def setup_page():
    st.set_page_config(
        page_title="Custom AI Chatbot",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# Modularizing sidebar options
def sidebar_options():
    catalog_options = ["Containers", "Models"]
    catalog_options_icon = ["box", "robot"]

    with st.sidebar:
        selected_catalog_option = option_menu(
            menu_title="Explore Catalog",
            menu_icon="cast",
            options=catalog_options,
            icons=catalog_options_icon,
        )

    st.sidebar.header("Use Case")
    use_cases = ["Select use case","Question Answering", "Retrieval Augmented Generation"]
    selected_use_cases = st.sidebar.selectbox(
        "Use Case", use_cases, label_visibility="collapsed"
    )

    # Chatbot icon button
    st.sidebar.markdown("---")



    if st.sidebar.button("🤖 Open Chatbot"):
        st.session_state.show_chatbot = True

    return selected_catalog_option, selected_use_cases


def display_container(title, description, tags, url):
    st.markdown(
        f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border: 1px solid #e1e1e1; padding: 10px; margin: 10px; border-radius: 5px;">
        <div>
            <h3 style="margin-bottom: 5px;">{title}</h3>
            <p>{description}</p>
            <span style="background-color: #e1e1e1; padding: 5px; border-radius: 3px;">{tags}</span>
        </div>
        <a href="{url}" target="_blank"><button style="margin-top: 10px;">Try Now</button></a>
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_model(title, description,url):
    st.markdown(
        f"""
    <div style="border: 1px solid #e1e1e1; padding: 10px; margin: 10px; border-radius: 5px;">
        <h3 style="margin-bottom: 5px;">{title}</h3>
        <p>{description}</p>
        <span style=" padding: 5px; border-radius: 3px;"></span>
        <a href="{url}" target="_blank"><button style="margin-top: 10px;">Try Now</button></a>
    </div>
    """,
        unsafe_allow_html=True,
    )

def check_use_case(selected_use_cases, containers):
    new_containers = []
    if "Retrieval Augmented Generation" in selected_use_cases:
        new_containers.append(containers[1])
        new_containers.append(containers[3])
    elif "Question Answering" in selected_use_cases:
        new_containers.append(containers[0])
        new_containers.append(containers[2])
    else:
        new_containers = containers
    return new_containers


def sample_chatbot():
    config = {"temperature": 0.1, "context_length": 8192}
    llm = CTransformers(
        model="TheBloke/neural-chat-7B-v3-1-GGUF",
        model_file="neural-chat-7b-v3-1.Q4_K_M.gguf",
        config=config,

)
    col1, col2 = st.columns([6,1])

    with col1:
        st.title("Generic Chatbot")
    with col2:
        if st.button("❌ Close"):
            st.session_state.show_chatbot = False

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = llm(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})




# Main function to control the flow
def main():
    startup()
    setup_page()
    selected_catalog_option, selected_use_cases = sidebar_options()

    if st.session_state.get("show_chatbot"):
        sample_chatbot()
    else:
        filtered_containers = check_use_case(selected_use_cases, containers)

        if selected_catalog_option == "Containers":
            st.title("Containers")
            for container in filtered_containers:
                display_container(
                    container["title"],
                    container["description"],
                    container["tags"],
                    container["url"],
                )

        elif selected_catalog_option == "Models":
            st.title("Models")
            for model in models:
                display_model(
                    model["title"],
                    model["description"],
                    model["url"],
                )

if __name__ == "__main__":
    main()
