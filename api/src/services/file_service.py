"""
File service for handling file uploads and attachments.

Manages file validation, storage, and metadata for chat attachments.
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import UploadFile, HTTPException

from api.src.utils.logging import logger
from api.src.utils.config import get_settings


class FileService:
    """Service for managing file uploads and attachments."""
    
    def __init__(self):
        self.logger = logger
        self.settings = get_settings()
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Allowed file types and sizes
        self.allowed_extensions = {
            ".pdf", ".doc", ".docx", ".txt", ".csv", 
            ".xlsx", ".xls", ".png", ".jpg", ".jpeg"
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def save_file(
        self,
        file: UploadFile,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Save uploaded file and return metadata.
        
        Args:
            file: Uploaded file
            user_id: User uploading the file
            
        Returns:
            File metadata dictionary
        """
        try:
            # Validate file
            await self._validate_file(file)
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create metadata
            metadata = {
                "id": str(uuid.uuid4()),
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "file_path": str(file_path),
                "content_type": file.content_type,
                "size": len(content),
                "user_id": user_id,
                "file_type": self._get_file_type(file_extension)
            }
            
            self.logger.info(
                "File saved successfully",
                file_id=metadata["id"],
                filename=file.filename,
                size=metadata["size"],
                user_id=user_id
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(
                "Failed to save file",
                error=str(e),
                filename=file.filename,
                user_id=user_id,
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    
    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. "
                       f"Allowed types: {', '.join(self.allowed_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size: {self.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Check for malicious content (basic check)
        if self._is_potentially_malicious(content):
            raise HTTPException(
                status_code=400,
                detail="File content appears to be potentially malicious"
            )
    
    def _get_file_type(self, extension: str) -> str:
        """Get file type category based on extension."""
        document_types = {".pdf", ".doc", ".docx", ".txt"}
        spreadsheet_types = {".csv", ".xlsx", ".xls"}
        image_types = {".png", ".jpg", ".jpeg"}
        
        if extension in document_types:
            return "document"
        elif extension in spreadsheet_types:
            return "spreadsheet"
        elif extension in image_types:
            return "image"
        else:
            return "other"
    
    def _is_potentially_malicious(self, content: bytes) -> bool:
        """Basic check for potentially malicious content."""
        # Check for executable signatures
        malicious_signatures = [
            b"MZ",  # PE executable
            b"\x7fELF",  # ELF executable
            b"PK\x03\x04",  # ZIP (could contain malicious files)
        ]
        
        for signature in malicious_signatures:
            if content.startswith(signature):
                return True
        
        return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info("File deleted successfully", file_path=file_path)
                return True
            return False
        except Exception as e:
            self.logger.error(
                "Failed to delete file",
                error=str(e),
                file_path=file_path,
                exc_info=True
            )
            return False