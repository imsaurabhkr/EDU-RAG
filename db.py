import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")

def get_google_api_key():
    return os.getenv("GOOGLE_API_KEY")


def get_mongo_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION_NAME]

def get_mongo_uri():
    return MONGO_URI

def get_db_name():
    return DB_NAME

def get_collection_name():
    return COLLECTION_NAME

def get_index_name():
    return ATLAS_VECTOR_SEARCH_INDEX_NAME
