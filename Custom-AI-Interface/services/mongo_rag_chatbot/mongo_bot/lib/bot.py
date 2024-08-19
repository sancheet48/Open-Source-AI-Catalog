"""Query BOT module."""
import argparse
import json
import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from time import time


import chromadb
from chromadb.config import Settings
from fastapi.responses import JSONResponse
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from mongo_bot import const
from mongo_bot.lib import output_modifier
from mongo_bot.lib.llm_models import LLM_MODEL
from mongo_bot.vector_db.vector_db_models import EMBEDDING_FUNCTION




logger = logging.getLogger(__file__)




# Template for Intel Neural chat 7B
LLM_TEMPLATE = (
    "### System: \n You are a helpful assistant to convert text to "
    + "PyMongo query.Answer exactly in one line from the schema. "
    + "Generate a single PyMongo query for the question from schema below : "
    + "{schema} "
    + "\n### User: \n{question}"
    + "\n### Assistant:\n "
)




LLM_SCHEMA = None
CHAT_COLLECTION = None


LLM_PROMPT = PromptTemplate(
    template=LLM_TEMPLATE, input_variables=["question", "schema"]
)
LLM_CHAIN = LLMChain(prompt=LLM_PROMPT, llm=LLM_MODEL)
# LLM_CHAIN = LLMChain(prompt=LLM_PROMPT | LLM_MODEL



def startup():
    """Startup function validator."""
    global LLM_SCHEMA, CHAT_COLLECTION
    if not const.CHROMA_DB_PATH:
        logger.warning(
            "Environment variables: 'CHROMA_DB_PATH' not defined. "
            + "Examples will not be added in prompt.",
        )
    if not const.SERVICE_COM_TOKEN:
        logger.warning(
            "Environment variable 'SERVICE_COM_TOKEN' not set, "
            + "token check will be disabled"
        )
    if not os.path.isfile(const.LLM_SCHEMA_PATH):
        logger.error(f"'{const.LLM_SCHEMA_PATH}' file not found")
        sys.exit(-1)
    logger.info("Loading LLM Schema")
    with open(const.LLM_SCHEMA_PATH) as file_p:
        LLM_SCHEMA = file_p.read()


    if const.CHROMA_DB_PATH:
        if not os.path.isdir(const.CHROMA_DB_PATH):
            logger.error("'%s' directory not found", const.CHROMA_DB_PATH)
            sys.exit(-1)


        chroma_client = chromadb.PersistentClient(
            path=const.CHROMA_DB_PATH,
            settings=Settings(allow_reset=True, anonymized_telemetry=False),
        )
        CHAT_COLLECTION = chroma_client.get_collection(
            name="chat_collection", embedding_function=EMBEDDING_FUNCTION
        )




def shutdown():
    """Teardown function."""
    ...




def retrieve_vdb(query: str) -> str:
    """Load the vectordb from local path and return the examples.


    Args:
        query (str): The question to be asked.


    Returns:
        str: Gives the nearest examples for the corresponding input query.
    """
    if not CHAT_COLLECTION:
        return ""
    query_result = CHAT_COLLECTION.query(query_texts=query, n_results=2)


    output_string = ""


    for document, metadata in zip(
        query_result["documents"][0], query_result["metadatas"][0]
    ):
        input_text = document
        response = metadata["response"]
        output_string += (
            f"{{\n"
            f"    'input': '{input_text}',\n"
            f"    'response': '{response}'\n"
            f"}},\n"
        )


    # Removing the trailing comma and newline
    output_string = output_string.rstrip(",\n")


    return output_string




def model_output(input_question: str, examples: str) -> tuple:
    """Get the corresponding mongo query for the input question.


    Args:
        input_question (str): The question to be asked
        examples (str): The examples to be added in the prompt.


    Returns:
        str: Gives the answer for the corresponding input query.
    """
    logging.info("User query: '%s'", input_question)
    start_time = time()
    response = LLM_CHAIN.run(
        {"question": input_question, "schema": LLM_SCHEMA + examples}
    )
    time_taken = time() - start_time
    logging.info("LLM response: '%s'", response)
    api_response = get_api_response_template()
    api_response["model_response"] = response
    api_response["time_taken"] = time_taken
    return api_response




def get_api_response_template() -> dict:
    """Get API response template.


    Returns:
        dict: Response template
    """
    return {
        "model_response": "",
        "mongodb_method": "",
        "mongodb_query": {},
        "mongodb_projection": {},
        "mongodb_field_name": "",
        "time_taken": 0,
        # "hostname": const.HOSTNAME,
    }




def is_valid_json(json_str) -> bool:
    """Check if a string is a valid json."""
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False




def get_query_and_projection(query):
    """Get the query and projection part for find mongo query."""
    word_to_replace = "True"
    replacement_word = "1"


    # Perform case-insensitive replace
    query = re.compile(re.escape(word_to_replace), re.IGNORECASE).sub(
        replacement_word, query
    )
    response_array = []
    count = 0
    i = 0
    while i < len(query):
        if query[i] == "{":
            for j in range(i + 1, len(query)):
                if query[j] == "}":
                    # pylint: disable=E203
                    if is_valid_json(query[i : j + 1]):  # noqa
                        response_array.append(query[i : j + 1])  # noqa
                        count += 1
                        i = j
                        break
        i += 1
    if len(response_array) >= 2:
        query = response_array[0]
        projection = response_array[1]
    elif len(response_array) == 1:
        query = response_array[0]
        projection = "{}"
    else:
        query = "{}"
        projection = "{}"


    return query, projection




def mongo_connect(api_response: dict) -> dict:
    """Get list of sytems for the given response.


    Args:
        response (str): Response for the given llm


    Returns:
        list: List of systems having the desired criteria.
    """
    # Create the MongoDB connection
    llm_response = api_response["model_response"]


    if len(llm_response.strip()) == 0:
        return api_response


    method = output_modifier.get_pymongo_method(llm_response)


    if "find" in method:
        logging.info("Running find query")
        query_string = output_modifier.get_find_query(
            output_modifier.get_pymongo_command(llm_response)
        )


        query, projection = get_query_and_projection(query_string)


        if not query:
            return api_response
        json_query = json.loads(query)
        json_projection = json.loads(projection)


        output_modifier.add_ignore_option_regex(json_query)


        api_response["mongodb_method"] = "find"
        api_response["mongodb_query"] = json_query
        api_response["mongodb_projection"] = json_projection
        return api_response
    if "aggregate" in method:
        logging.info("Running aggregate query")
        query = output_modifier.get_aggregate_query(
            output_modifier.get_pymongo_command(llm_response)
        )
        logging.info("Query: %s", query)
        json_query = json.loads(query)


        logging.info("JSON Query: %s", json_query)
        api_response["mongodb_method"] = "aggregate"
        api_response["mongodb_query"] = json_query
        return api_response


    if "countDocuments" in method:
        logging.info("Running countDocuments")
        _, query = output_modifier.format_output(llm_response)
        json_query = json.loads(query)
        api_response["mongodb_method"] = "countDocuments"
        api_response["mongodb_query"] = json_query
        return api_response


    if "find_one" in method:
        logging.info("Running find_one")
        _, query = output_modifier.format_output(llm_response)
        json_query = json.loads(query)
        api_response["mongodb_method"] = "find_one"
        api_response["mongodb_query"] = json_query
        return api_response


    if "distinct" in method:
        logging.info("Running distinct")
        # distinct(field, query)
        query = {}
        if "," in llm_response:
            field = llm_response[
                llm_response.find("(") + 1 : llm_response.find(",")  # noqa
            ]  # noqa
            _, query = output_modifier.format_output(llm_response)
        else:
            field = llm_response[
                llm_response.find("(") + 1 : llm_response.rfind(")")  # noqa
            ]  # noqa
            query = "{}"


        json_query = json.loads(query)
        for key, value in json_query.items():
            if isinstance(value, str):
                json_query[key] = {"$regex": value, "$options": "i"}
        api_response["mongodb_method"] = "distinct"
        api_response["mongodb_query"] = json_query
        api_response["mongodb_field_name"] = (
            field.strip().strip('"').strip("'")
        )
        return api_response
    logging.error("No valid method found! ")
    return api_response




def get_db_query(query: str) -> dict:
    """Get System from query.


    Args:
        query (str): Natural Language Query


    Returns:
        list: List of systems
    """
    examples = retrieve_vdb(query)


    api_response = model_output(query, examples)
    try:
        api_response = mongo_connect(api_response)
    except Exception as expt:
        logger.error("Exception: %s", expt)
        return JSONResponse(content=api_response, status_code=400)
    return JSONResponse(content=api_response, status_code=200)




def main():
    """Test functionality manually."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(module)s:%(lineno)d"
        + " | %(message)s",
        handlers=[
            RotatingFileHandler(
                f"{os.path.join(const.PROJECT_DIR, 'bot.log')}",
                maxBytes=256 * 1024,
                backupCount=1,
                encoding="utf8",
            ),
            logging.StreamHandler(),
        ],
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="User Query", required=True)
    args = parser.parse_args()
    query = args.query
    startup()
    print(get_db_query(query))


    shutdown()




if __name__ == "__main__":
    main()


