# main.py sits in your root folder
from application.service.semantic_search_service import TraceabilityService
from application.service.engine import SemanticEngine
from application.web.controller import router
from fastapi import FastAPI
import uvicorn
from application.repo.db import get_connection
from application.repo.TensorRepository import TensorRepository
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()
conn = get_connection()
repo = TensorRepository(conn)
engine = SemanticEngine(repo)
traceability_service = TraceabilityService(engine)
app.state.traceability_service = traceability_service

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
