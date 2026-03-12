# main.py sits in your root folder
from application.service.semantic_search_service import TraceabilityService
from application.service.engine import SemanticEngine
from application.schemas.schema import Requirement, TestCase
from application.web.controller import router
import json
from fastapi import FastAPI
import uvicorn

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
