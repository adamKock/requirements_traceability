from fastapi import APIRouter
from fastapi import FastAPI
from application.schemas.schema import Requirement, TestCase
from fastapi import UploadFile, File, Depends, HTTPException
from contextlib import asynccontextmanager
import time
import httpx
import uuid
from redis import Redis 
from application.web.dependancies import get_service

app= FastAPI()

async def lifespan(app: FastAPI):
    app.state.redis = Redis(host='localhost', port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield 
    print("App Finished Pre Run")
    await app.state.redis.aclose()
    print("Redis connection closed safely")

    
