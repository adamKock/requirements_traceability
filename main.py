# main.py sits in your root folder
from application.service.semantic_search_service import TraceabilityService
from application.service.engine import SemanticEngine
from application.schemas.schema import Requirement, TestCase
import json
from fastapi import FastAPI
from application.web.controller import router

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    engine = SemanticEngine()
    service = TraceabilityService()
    
    try:
        requirements = service.import_csv("requirements.csv", Requirement)
        test_cases = service.import_csv("test_cases.csv", TestCase)
        payload = service.build_payload(requirements, test_cases)


        similarity = service.convert_to_tensor(payload)
        results = service.compare(payload, similarity)
       

        if results:
            print(f"SUCCESS: Data Loaded")
            print(json.dumps(results, indent=4))
            
    except Exception as e:
        print(f"ERROR: {e}")
