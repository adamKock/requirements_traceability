from fastapi import APIRouter
from fastapi import APIRouter, FastAPI, UploadFile, File, Depends, HTTPException, Request
from application.schemas.schema import Requirement, TestCase
from fastapi import UploadFile, File, Depends, HTTPException
from contextlib import asynccontextmanager
import time
import httpx
import uuid
import json
import redis.asyncio as redis
from application.web.dependancies import get_service


router = APIRouter()
#job_store={}
@asynccontextmanager
async def lifespan(app: FastAPI):
    service = app.state.traceability_service

    default_test_mapping = service.normalize_mapping({
            "id": ["id", "testcaseid"],
            "summary":["summary", "title"],
            "stepnumber":["teststep", "teststeps","step", "test steps","stepnumber"],
            "stepaction":["stepactions","stepaction"]
        })
  
    default_requirement_mapping=service.normalize_mapping({
            "id": ["id","requirementid"],
            "name": ["name","requirementname", "title","summary"],
            "description": ["description","requirementdescription"]
        })
    requirement_mapping = service.get_all_requirement_mappings()
    test_mapping = service.get_all_test_mappings()

   # Use the async client
    app.state.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    app.state.http_client = httpx.AsyncClient()

    if not test_mapping or not requirement_mapping:
        service.store_requirement_mappings(default_requirement_mapping)
        service.store_test_mappings(default_test_mapping)
    else:
        pass

    yield 
    print("App Finished Pre Run")

    await app.state.redis.aclose()
    print("Redis connection closed safely")

app = FastAPI(lifespan=lifespan)

@router.post("/validate_requirements")
async def validate_requirements(request: Request,service = Depends(get_service), requirements_file:UploadFile = File(...)):
    
    try:
        requirements_mapped = service.map_requirements(requirements_file.file)
        requirements_list = service.import_csv(requirements_mapped, Requirement)
        job_id = str(uuid.uuid4())

        job_data = {
            "requirements": [req.model_dump() for req in requirements_list],
            "test_cases_ready": False,
            "created_at": time.time()
        }

        await request.app.state.redis.hset("job_store", job_id, json.dumps(job_data))
        return {"status": "success", 
                "job_id": job_id, 
                "rows": len(requirements_list)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#This endpoint is for test case upload and storage to the DB 
@router.post("/validate/testcases/{job_id}")
async def validate_testcases(job_id:str, request: Request,testcases_file:UploadFile = File(...),service = Depends(get_service),):
    
    raw_job = await request.app.state.redis.hget("job_store", job_id)
    if not raw_job:
        raise HTTPException(status_code=404, detail="ID not found")
    job = json.loads(raw_job)
    
    #if job_id not in job_store:
        #raise HTTPException(status_code=404, detail="ID not found")
    try:
        test_cases_mapped = service.map_test_cases(testcases_file.file)
        test_cases_list = service.import_csv(test_cases_mapped, TestCase)
        service.store_test_cases(test_cases_list, job_id)
        #job_store[job_id]["test_cases_ready"] = True
        job["test_cases_ready"] = True
        await request.app.state.redis.hset("job_store", job_id, json.dumps(job))
        
        return {"status": "success", 
                "rows": len(test_cases_list)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#This endpoint takes the requirements in the job store creates embeddings then runs similaritys against them
#vs embeddings in the DB for the test cases 
@router.post("/submit/{job_id}")
async def submit(job_id:str,request: Request, service = Depends(get_service)):
    
    raw_job = await request.app.state.redis.hget("job_store", job_id)
    if not raw_job:
        raise HTTPException(status_code=404, detail="ID not found")
    
    #if job_id not in job_store:
        #raise HTTPException(status_code=404, detail="ID not found")
    
    #job = job_store[job_id]
    job = json.loads(raw_job)

    if not job.get("test_cases_ready"):
        raise HTTPException(status_code=400, detail="Test cases not validated")
    
    if not job["requirements"]:
        raise HTTPException(status_code=400, detail="Requirements not validated")

    try:
        req_objects = [Requirement(**r) for r in job["requirements"]]
        results = service.run_traceability(req_objects, job_id)
        #results = service.run_traceability(job["requirements"],job_id)
        await request.app.state.redis.hdel("job_store", job_id)
        #del job_store[job_id]
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        


