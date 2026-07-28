"""
Router: /api/v1/upload

Endpoint para subir imágenes (avatars, metas, etc.).
"""

import base64
import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user
from app.core.exceptions import ValidationException
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Sube una imagen y la retorna como data URI base64."""
    if file.content_type not in ALLOWED_TYPES:
        raise ValidationException(
            f"Tipo de archivo no permitido. Usa: {', '.join(ALLOWED_TYPES)}"
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise ValidationException(
            f"Archivo demasiado grande. Máximo {MAX_SIZE_MB}MB."
        )

    b64 = base64.b64encode(contents).decode("utf-8")
    data_uri = f"data:{file.content_type};base64,{b64}"

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"url": data_uri, "content_type": file.content_type},
    )
