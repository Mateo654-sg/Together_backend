"""
Router: /api/v1/upload

Sube imágenes a AWS S3 y devuelve la URL pública permanente.
Los archivos se almacenan bajo el prefijo `avatars/` con nombre único (UUID).
"""

import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import AppException, ValidationException
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
MAX_SIZE_MB = 5


def _s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Sube una imagen a S3 y retorna su URL pública.

    - Valida tipo MIME y tamaño antes de subir.
    - El archivo se guarda en `avatars/<uuid>.<ext>` para evitar colisiones.
    - La URL devuelta es permanente y sirve directamente desde S3.
    """
    if not settings.aws_access_key_id or not settings.s3_bucket:
        raise AppException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="El servicio de almacenamiento no está configurado.",
        )

    if file.content_type not in ALLOWED_TYPES:
        raise ValidationException(
            f"Tipo de archivo no permitido. Usa: {', '.join(ALLOWED_TYPES)}"
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise ValidationException(f"Archivo demasiado grande. Máximo {MAX_SIZE_MB}MB.")

    ext = EXTENSIONS[file.content_type]
    key = f"avatars/{uuid.uuid4()}.{ext}"

    try:
        s3 = _s3_client()
        s3.put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError) as exc:
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message="No se pudo subir la imagen. Intenta nuevamente.",
        ) from exc

    url = f"https://{settings.s3_bucket}.s3.amazonaws.com/{key}"

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"url": url, "content_type": file.content_type},
    )
