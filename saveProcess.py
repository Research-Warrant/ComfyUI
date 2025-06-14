import os
from pymongo import MongoClient
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

def saveProcess(prompt_id, process):
    databaseUri = os.getenv("DATABASE_URI")
    databaseUser = os.getenv("DATABASE_USER")
    databasePass = os.getenv("DATABASE_PASS")
    databaseName = os.getenv("DATABASE_NAME")

    try:
        client = MongoClient(
            databaseUri,
            username=databaseUser,
            password=databasePass
        )
        db = client[databaseName]
        collection = db["auditlogs"]

        log_entry = {
            "created_on": datetime.utcnow().isoformat(),
            "process": process,
        }

        result = collection.update_one(
            {"hash": prompt_id},
            {"$set": log_entry},
            upsert=True
        )
        if result.matched_count > 0:
            print("Log updated successfully.")
        else:
            print("New log entry created.")

        print("Updated ID:", result)
    except Exception as e:
        print(f"[SaveProcess] Error inserting log: {e}")