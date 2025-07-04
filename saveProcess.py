from db import get_mongo_client
from datetime import datetime
import os

def saveProcess(prompt_id, process, error=None):
    try:
        print(f"[SaveProcess] Saving process for prompt ID: {prompt_id} with process: {process}")
        client = get_mongo_client()
        db = client[os.getenv("DATABASE_NAME")]
        collection = db["auditlogs"]

        log_entry = {
            "created_on": datetime.utcnow().isoformat(),
            "process": process,
        }
        if error:
            log_entry["error"] = error        

        result = collection.update_one(
            {"hash": prompt_id},
            {"$set": log_entry},
            upsert=True
        )

        if result.matched_count > 0:
            print("Log updated successfully.")
        else:
            print("New log entry created.")

    except Exception as e:
        print(f"[SaveProcess] Error inserting log: {e}")
