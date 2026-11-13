import os
import uuid
from typing import Optional, Tuple
from fastapi import HTTPException, status
from src.core.config import settings

ERROR_LOGO_SIZE_EXCEEDED = "El archivo del logo no puede exceder los 2 MB"
ERROR_LOGO_INVALID_TYPE = "Solo se permiten imágenes en formato PNG, JPG o WEBP"

# Magic bytes signatures
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
RIFF_MAGIC = b"RIFF"
WEBP_MAGIC = b"WEBP"


class LogoStorageService:
    def __init__(
        self,
        upload_dir: Optional[str] = None,
        max_size_bytes: Optional[int] = None,
    ):
        self.upload_dir = upload_dir or settings.LOGO_UPLOAD_DIR
        self.max_size_bytes = (
            max_size_bytes
            if max_size_bytes is not None
            else settings.LOGO_MAX_SIZE_BYTES
        )
        os.makedirs(self.upload_dir, exist_ok=True)

    def detect_image_type(self, data: bytes) -> Optional[str]:
        """
        Validates the real image signature from byte header.
        Returns the appropriate file extension (.png, .jpg, .webp) or None.
        """
        if len(data) < 12:
            return None

        if data.startswith(PNG_MAGIC):
            return ".png"
        if data.startswith(JPEG_MAGIC):
            return ".jpg"
        if data.startswith(RIFF_MAGIC) and data[8:12] == WEBP_MAGIC:
            return ".webp"

        return None

    def save_logo_file(
        self,
        file_bytes: bytes,
        previous_logo_url: Optional[str] = None,
    ) -> str:
        """
        Validates size and magic bytes, saves the file with a UUID-based name,
        cleans up any previous local logo, and returns the public URL path.
        """
        # 1. Size check
        if len(file_bytes) > self.max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_LOGO_SIZE_EXCEEDED,
            )

        # 2. Signature check
        ext = self.detect_image_type(file_bytes)
        if not ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_LOGO_INVALID_TYPE,
            )

        # 3. Save new file
        filename = f"{uuid.uuid4().hex}{ext}"
        destination_path = os.path.join(self.upload_dir, filename)
        with open(destination_path, "wb") as f:
            f.write(file_bytes)

        # 4. Remove previous local file if applicable
        if previous_logo_url:
            self._delete_local_logo(previous_logo_url)

        # 5. Return web URL
        normalized_url = f"/static/logos/{filename}"
        return normalized_url

    def _delete_local_logo(self, logo_url: str) -> None:
        if logo_url and logo_url.startswith("/static/logos/"):
            prev_filename = os.path.basename(logo_url)
            prev_path = os.path.join(self.upload_dir, prev_filename)
            if os.path.exists(prev_path):
                try:
                    os.remove(prev_path)
                except OSError:
                    pass

