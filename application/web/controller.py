#NDifferemt endpoints we need 

#Upload endpoint 
#Submit the engine endpoint

from fastapi import APIRouter
from pydantic import BaseModel
from application.schemas.schema import Requirement, TestCase
from application.service.semantic_search_service import TraceabilityService
from fastapi import UploadFile, File, Depends, HTTPException
import time
import uuid

router = APIRouter()
traceability_service = TraceabilityService()

job_store={}


@router.post("/validate_requirements")
def validate_requirements(requirements_file:UploadFile = File(...)):
    try:
        requirements_list = traceability_service.import_csv(requirements_file.file, Requirement)
        job_id = str(uuid.uuid4())

        job_store[job_id] = {
            "requirements": requirements_list,
            "test_cases": None,
            "created_at": time.time()
        }
        return {"status": "success", 
                "job_id": job_id, 
                "rows": len(requirements_list)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/validate/testcases/{job_id}")
def validate_testcases(job_id:str, testcases_file:UploadFile = File(...)):

    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="ID not found")
    try:
        test_cases_list = traceability_service.import_csv(testcases_file.file, TestCase)
        job_store[job_id]["test_cases"] = test_cases_list
        return {"status": "success", 
                "rows": len(test_cases_list)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit/{job_id}")
def submit(job_id:str):
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="ID not found")
    try:
        job = job_store[job_id]

        if not job["requirements"] or not job["test_cases"]:
            raise HTTPException(status_code=400, detail="Both files must be validated before submitting")
        
        payload = traceability_service.build_payload(job["requirements"], job["test_cases"])
        tensor_data = traceability_service.convert_to_tensor(payload)
        results = traceability_service.compare(payload, tensor_data)
        del job_store[job_id]
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        

     



