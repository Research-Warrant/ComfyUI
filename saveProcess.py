from db import get_mongo_client
from datetime import datetime
import os

def saveProcess(prompt_id, process, error=None):
    try:
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
            pass
        else:
            pass

    except Exception:
        pass
