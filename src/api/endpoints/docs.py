from datetime import datetime 
import os
from typing import Annotated, List, Optional
from fastapi import APIRouter, FastAPI, File, Form, UploadFile
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

@router.post('/generate')
async def generate(
        service: str = Form(...),
        promptText: str = Form(...),
        pageAnalysis: str = Form(...),
        pageResult: str = Form(...),
        pageUseCase: str = Form(...),
        files: list[UploadFile] = File(...),
    ):
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d-%M_%S")
    save_directory = f'./public/{formatted_date}/'
    # Ensure the directory exists
    os.makedirs(save_directory, exist_ok=True)

    for file in files:
        contents = await file.read()
        # Save the file or process it as needed
        file_path = os.path.join(save_directory, file.filename)
        with open(file_path, 'wb') as f:
            f.write(contents)
            
    return {"message": "Files successfully uploaded", "service": service}