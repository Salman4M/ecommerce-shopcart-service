"""
Final working main.py
src/main.py
"""
from fastapi import FastAPI
from src.shopcart_service.core.db import Base, engine
from src.shopcart_service.api.v1 import routes as routes_v1

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shopcart Service",
    description="Shopping Cart Microservice with Gateway Authentication",
    version="1.0.0"
)

app.include_router(routes_v1.router)


@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint
    No authentication required
    """
    return {"message": "Shopcart Service is running", "status": "healthy"}


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check for Cloud Run
    No authentication required
    """
    return {"status": "healthy"}