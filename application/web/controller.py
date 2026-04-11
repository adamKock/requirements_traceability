from fastapi import APIRouter
from fastapi import FastAPI
from application.schemas.schema import Requirement, TestCase
from fastapi import UploadFile, File, Depends, HTTPException
from contextlib import asynccontextmanager
import time
import uuid
from application.web.dependancies import get_service


router = APIRouter()
job_store={}
@asynccontextmanager
async def lifespan(app: FastAPI):
    service = app.state.traceability_service
    default_test_mapping = {
            "id": ["id", "ID", "iD", "Id", "testcaseid"],
            "summary":["Summary", "Title", "title"],
            "stepnumber":["teststep", "teststeps","step", "Test Steps"],
            "stepaction":["stepactions","StepAction"]
        }
    
    default_requirement_mapping={
            "id": ["id", "ID", "iD", "Id", "requirementid"],
            "name": ["name", "Name", "requirementname", "title", "Title", "summary", "Summary"],
            "description": ["description", "Description", "requirementdescription", "description", "Description"]
        }
    requirement_mapping = service.get_all_requirement_mappings()
    test_mapping = service.get_all_test_mappings()

    if not test_mapping or not requirement_mapping:
        service.store_requirement_mappings(default_requirement_mapping)
        service.store_test_mappings(default_test_mapping)
    else:
        pass

    yield 
    print("App Finished Pre Run")

app = FastAPI(lifespan=lifespan)

@router.post("/validate_requirements")
def validate_requirements(service = Depends(get_service), requirements_file:UploadFile = File(...)):
    
    try:
        requirements_mapped = service.map_requirements(requirements_file.file)
        requirements_list = service.import_csv(requirements_mapped, Requirement)
        job_id = str(uuid.uuid4())

        job_store[job_id] = {
            "requirements": requirements_list,
            "test_cases_ready": False,
            "created_at": time.time()
        }
        return {"status": "success", 
                "job_id": job_id, 
                "rows": len(requirements_list)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#This endpoint is for test case upload and storage to the DB 
@router.post("/validate/testcases/{job_id}")
def validate_testcases(job_id:str, testcases_file:UploadFile = File(...),service = Depends(get_service),):

    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="ID not found")
    try:
        test_cases_mapped = service.map_test_cases(testcases_file.file)
        test_cases_list = service.import_csv(test_cases_mapped, TestCase)
        service.store_test_cases(test_cases_list, job_id)
        job_store[job_id]["test_cases_ready"] = True
        
        return {"status": "success", 
                "rows": len(test_cases_list)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#This endpoint takes the requirements in the job store creates embeddings then runs similaritys against them
#vs embeddings in the DB for the test cases 
@router.post("/submit/{job_id}")
def submit(job_id:str, service = Depends(get_service)):
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="ID not found")
    
    job = job_store[job_id]

    if not job.get("test_cases_ready"):
        raise HTTPException(status_code=400, detail="Test cases not validated")
    
    if not job["requirements"]:
        raise HTTPException(status_code=400, detail="Requirements not validated")

    try:
        results = service.run_traceability(job["requirements"],job_id)
        
        del job_store[job_id]
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        

     



