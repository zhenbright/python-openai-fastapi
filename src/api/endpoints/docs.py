from fastapi import APIRouter, FastAPI
from src.utils.logging_config import CustomLogger
from starlette.responses import RedirectResponse


# Get the logger instance from the CustomLogger class
logger = CustomLogger().get_logger

# Create a new APIRouter instance
router = APIRouter()

# Create a FastAPI application
app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})

# Define a Docmentation endpoint
@router.get("/")
async def root():
    return RedirectResponse(app.docs_url)
    