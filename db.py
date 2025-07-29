import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_client = None

def init_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(
            os.getenv("DATABASE_URI"),
            username=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASS")
        )
        print("✅ MongoDB client initialized")
    return mongo_client

def get_mongo_client():
    if mongo_client is None:
        raise Exception("Mongo client not initialized")
    return mongo_client