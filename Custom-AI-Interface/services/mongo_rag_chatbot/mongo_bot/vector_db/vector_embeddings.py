"""Function to create Vector DB."""
import argparse
import os
import shutil


import chromadb
from chromadb.config import Settings
from pymongo.mongo_client import MongoClient
from query_bot.vector_db.vector_db_models import EMBEDDING_FUNCTION


def create_vector_db(
    connection_string: str,
    db_name: str,
    collection_name: str,
    vector_db_path: str,
):
    """Create Vector DB from Mongo DB.


    Args:
        connection_string (str): The connection string for the MongoDB.
        db_name (str): The name of the MongoDB database.
        collection_name (str): The name of the MongoDB collection.
        vector_db_path (str): The path to store the vector DB.
    """
    if os.path.isdir(vector_db_path):
        print("Removing existing vector db path.")
        shutil.rmtree(vector_db_path)


    print(f"Loading documents from MongoDB {db_name}")
    client = MongoClient(connection_string)
    mongo_db = client[db_name]
    mongo_collection = mongo_db[collection_name]


    query = {}
    projection = {"_id": False}


    cursor = mongo_collection.find(query, projection)


    mongo_documents_input = []
    mongo_documents_response = []


    for ele in list(cursor):


        response_dict = {}  # since the metadata has to be dict or None


        response_dict["response"] = ele["response"]
        mongo_documents_input.append(ele["input"])
        mongo_documents_response.append(response_dict)


    print("Computing Vectors")
    chroma_client = chromadb.PersistentClient(
        path=vector_db_path,
        settings=Settings(allow_reset=True, anonymized_telemetry=False),
    )
    chat_collection = chroma_client.create_collection(
        name="chat_collection", embedding_function=EMBEDDING_FUNCTION
    )
    ids = [str(i) for i in range(len(mongo_documents_input))]


    chat_collection.add(
        documents=mongo_documents_input,
        metadatas=mongo_documents_response,
        ids=ids,
    )


    print(f"Embedding are succesfully stored in {vector_db_path}")




def main():
    """Create Vector DB."""
    parser = argparse.ArgumentParser(
        description="Create vector database from MongoDB."
    )
    parser.add_argument(
        "--connection_string", required=True, help="MongoDB connection string."
    )
    parser.add_argument(
        "--db_name", required=True, help="MongoDB database name."
    )
    parser.add_argument(
        "--collection_name", required=True, help="MongoDB collection name."
    )
    parser.add_argument(
        "--vector_db_path", required=True, help="Vector DB Path."
    )


    args = parser.parse_args()


    create_vector_db(
        args.connection_string,
        args.db_name,
        args.collection_name,
        args.vector_db_path,
    )




if __name__ == "__main__":
    main()
