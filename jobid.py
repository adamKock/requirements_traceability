import time
import uuid



job_store={} 



for x in range(3):
    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "requirements": None,
        "test_cases": None,
        "created_at": time.time()
    }



print(job_store[job_id]["requirements"])