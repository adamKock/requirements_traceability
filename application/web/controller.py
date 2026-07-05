from fastapi import APIRouter, FastAPI, UploadFile, File, Depends, HTTPException, Request
from application.schemas.schema import Requirement, TestCase
from fastapi import UploadFile, File, Depends, HTTPException
from contextlib import asynccontextmanager
import time
import httpx
import uuid
import json
import redis.asyncio as redis
from application.web.dependencies import get_traceability_service
from application.repo.db import open_pool, close_pool
import os
from application.web.auth import verify_api_key




router = APIRouter(dependencies=[Depends(verify_api_key)])
JOB_TTL_SECONDS = 60 * 60 * 24  # 24 hours — adjust to whatever makes sense for your workflow
def job_key(job_id: str) -> str:
    return f"job:{job_id}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_pool()

    service = app.state.traceability_service
    repo = app.state.repo

    await repo.initialize_schema()
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
    
    requirement_mapping = await service.get_all_requirement_mappings()
    test_mapping = await service.get_all_test_mappings()

    if not test_mapping or not requirement_mapping:
        await service.store_requirement_mappings(default_requirement_mapping)
        await service.store_test_mappings(default_test_mapping)
    else:
        pass
    # Use the async client
    app.state.redis = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)
    app.state.http_client = httpx.AsyncClient()
    yield 
    print("App Finished Pre Run")

    await app.state.redis.aclose()
    await app.state.http_client.aclose()
    await close_pool()
    print("Redis connection closed safely")


@router.post("/validate_requirements")
async def validate_requirements(request: Request,service = Depends(get_traceability_service), requirements_file:UploadFile = File(...)):
    
    try:
        requirements_mapped = await service.map_requirements(requirements_file.file)
        requirements_list = await service.import_csv(requirements_mapped, Requirement)
        job_id = str(uuid.uuid4())

        job_data = {
            "requirements": [req.model_dump() for req in requirements_list],
            "test_cases_ready": False,
            "created_at": time.time()
        }

        await request.app.state.redis.setex(job_key(job_id), JOB_TTL_SECONDS, json.dumps(job_data))
        return {"status": "success", 
                "job_id": job_id, 
                "rows": len(requirements_list)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#This endpoint is for test case upload and storage to the DB 
@router.post("/validate/testcases/{job_id}")
async def validate_testcases(job_id:str, request: Request,testcases_file:UploadFile = File(...),service = Depends(get_traceability_service)):
    
    raw_job = await request.app.state.redis.hget("job_store", job_id)
    if not raw_job:
        raise HTTPException(status_code=404, detail="ID not found")
    job = json.loads(raw_job)
    
  
    try:
        test_cases_mapped = await service.map_test_cases(testcases_file.file )
        test_cases_list = await service.import_csv(test_cases_mapped, TestCase)
        await service.store_test_cases(test_cases_list, job_id)
        job["test_cases_ready"] = True
        await request.app.state.redis.setex(job_key(job_id), JOB_TTL_SECONDS, json.dumps(job))

        
        return {"status": "success", 
                "rows": len(test_cases_list)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#This endpoint takes the requirements in the job store creates embeddings then runs similaritys against them
#vs embeddings in the DB for the test cases 
@router.post("/submit/{job_id}")
async def submit(job_id:str,request: Request, service = Depends(get_traceability_service)):
    
    raw_job = await request.app.state.redis.hget("job_store", job_id)
    if not raw_job:
        raise HTTPException(status_code=404, detail="ID not found")
    
    job = json.loads(raw_job)

    if not job.get("test_cases_ready"):
        raise HTTPException(status_code=400, detail="Test cases not validated")
    
    if not job["requirements"]:
        raise HTTPException(status_code=400, detail="Requirements not validated")

    try:
        req_objects = [Requirement(**r) for r in job["requirements"]]
        results = await service.run_traceability(req_objects, job_id)
        await request.app.state.redis.hdel("job_store", job_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        


