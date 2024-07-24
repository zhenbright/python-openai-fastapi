from fastapi import APIRouter, FastAPI, File, Form, UploadFile
from src.service.FileService import FileService
from src.utils.logging_config import CustomLogger
from starlette.responses import RedirectResponse
from src.service.GenerateService import GenerateService

# Get the logger instance from the CustomLogger class
logger = CustomLogger().get_logger

# Create a new APIRouter instance
router = APIRouter()

# Create a FastAPI application
app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})

# Import Services
generate_service = GenerateService()
file_service = FileService()
# Define a Docmentation endpoint
@router.get("/")
async def root():
    return RedirectResponse(app.docs_url)

@router.post('/generate')
async def generate(
        service: str = Form(...),
        promptText: str = Form(...),
        pageAnalysis: str = Form(...),
        pageResult: str = Form(...),
        pageUseCase: str = Form(...),
        files: list[UploadFile] = File(...),
    ):
    
    file_paths = await file_service.uploadFiles(files)
    
    response = generate_service.generate(
        service,
        promptText,
        pageAnalysis,
        pageResult,
        pageUseCase,
        file_paths
    )            
    return response