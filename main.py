from application.service.semantic_search_service import TraceabilityService
from application.service.engine import SemanticEngine
from application.web.controller import lifespan, router
from fastapi import FastAPI
import uvicorn
from application.repo.TensorRepository import TensorRepository
from dotenv import load_dotenv

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("app")

load_dotenv()
app = FastAPI(lifespan=lifespan)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

repo = TensorRepository()
engine = SemanticEngine(repo)
traceability_service = TraceabilityService(engine, repo)

app.state.repo = repo
app.state.traceability_service = traceability_service
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)