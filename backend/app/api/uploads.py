import io
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile, _: User = Depends(get_current_user)):
    settings = get_settings()
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(415, "Only JPEG, PNG and WEBP images are allowed")
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"Image must be smaller than {settings.max_upload_mb} MB")
    try:  # verify real content, not just the declared content-type
        with Image.open(io.BytesIO(data)) as img:
            fmt = img.format
            img.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(415, "File is not a valid image") from None
    if fmt not in ALLOWED:
        raise HTTPException(415, "Only JPEG, PNG and WEBP images are allowed")
    name = f"{uuid.uuid4().hex}{ALLOWED[fmt]}"
    directory = Path(settings.upload_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_bytes(data)
    return {"image_url": f"/uploads/{name}"}
