import os
import sys
import logging
import streamlit as st
from streamlit_option_menu import option_menu
from logging.handlers import RotatingFileHandler
import const


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
    if not const.GENERIC_CHATBOT_URI:
        missing.append("GENERIC_CHATBOT_URI")
    if not const.RAG_CHATBOT_URI:
        missing.append("RAG_CHATBOT_URI")
        
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
    use_cases = ["Question Answering", "Retrieval Augmented Generation"]
    selected_use_cases = st.sidebar.multiselect(
        "Use Case", use_cases, label_visibility="collapsed"
    )

    st.sidebar.header("Solution")
    platforms = ["Conversational AI", "Languages and API"]
    selected_platforms = st.sidebar.multiselect(
        "Solutions", platforms, label_visibility="collapsed"
    )

    return selected_catalog_option, selected_use_cases, selected_platforms


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


def display_model(title, description, tags):
    st.markdown(
        f"""
    <div style="border: 1px solid #e1e1e1; padding: 10px; margin: 10px; border-radius: 5px;">
        <h3 style="margin-bottom: 5px;">{title}</h3>
        <p>{description}</p>
        <span style="background-color: #e1e1e1; padding: 5px; border-radius: 3px;">{tags}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Main function to control the flow
def main():
    startup()
    setup_page()
    selected_catalog_option, selected_use_cases, selected_platforms = sidebar_options()
    containers = [
        {
            "title": "General Purpose Chatbot",
            "description": "",
            "tags": "Generic Chatbot",
            "url": const.GENERIC_CHATBOT_URI,
        },
        {
            "title": "Retrieval Augmented Generation  Chatbot",
            "description": "",
            "tags": "Chat with your own custom data",
            "url": const.RAG_CHATBOT_URI,
        },
    ]

    models = [
        {
            "title": "Intel Neural Chat 7B",
            "description": "This model is a fine-tuned 7B parameter LLM on the Intel Gaudi 2 processor from the mistralai/Mistral-7B-v0.1 on the open source dataset Open-Orca/SlimOrca.",
            "tags": "INTEL AI Enterprise Supported",
        },
    ]

    if selected_catalog_option == "Containers":
        st.title("Containers")
        for container in containers:
            display_container(
                container["title"],
                container["description"],
                container["tags"],
                container["url"],
            )

    elif selected_catalog_option == "Models":
        st.title("Models")
        for model in models:
            display_model(model["title"], model["description"], model["tags"])


if __name__ == "__main__":
    main()
