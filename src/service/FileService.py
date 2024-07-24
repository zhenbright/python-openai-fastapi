from datetime import datetime
import os
from fastapi import File, UploadFile


class FileService:
    
    async def uploadFiles(
        self,
        files: list[UploadFile] = File(...)
    ):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d-%M_%S")
        save_directory = f'/public/{formatted_date}/'
        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)

        file_paths = []
        
        for file in files:
            contents = await file.read()
            # Save the file or process it as needed
            file_path = os.path.join(save_directory, file.filename)
            with open(file_path, 'wb') as f:
                f.write(contents)
                file_paths.append(file_path)
        return file_paths