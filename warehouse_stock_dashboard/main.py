from fastapi import FastAPI, HTTPException
from app.api import endpoints
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Dashboard API", debug=True)

# Add error logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response: {response.status_code}")
    return response

# Mount the router
logger.debug("Mounting API router at /api prefix")
app.include_router(endpoints.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "API is running"}