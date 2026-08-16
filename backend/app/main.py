from fastapi import FastAPI
from app.config import settings
from app.api.routes import router
from app.database.session import Base, engine
from app.database.models.appointment import Appointment
import logging
from app.core.logging import setup_logging
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
)


setup_logging()

logger = logging.getLogger(__name__)


# This creates your FastAPI application.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for the AI Receptionist project."
)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)

# Create database tables before initializing the FastAPI application.
Base.metadata.create_all(bind=engine)

#This defines a GET endpoint for the root URL.
@app.get("/")
def root():
    return {
         "message": f"Welcome to the {settings.APP_NAME}!",
         "deployment": "GitHub Action Build #1"
    }

# Endpoint used to verify that the application is running.
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }

app.include_router(router)
logger.info("Application initialized successfully")


# # temp api to test 
# @app.get("/test-error")
# def test_error():
#     raise AppException(
#         message="This is a test application error",
#         status_code=400,
#     )