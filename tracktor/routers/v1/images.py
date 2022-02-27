"""
V1 of the API - Images
"""
import base64
import io
from typing import IO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tracktor.error import ItemNotFoundException
from tracktor.models import Image
from tracktor.utils.database import get_session

router = APIRouter(prefix="/images")


@router.get("/{image_id}")
async def get_image(image_id: str, session: AsyncSession = Depends(get_session)):
    """
    Request to return all tracks
    """
    if requested_image := await Image.get_by_entity_id(
        entity_id=image_id, session=session
    ):
        decoded_image: IO[bytes] = io.BytesIO(base64.b64decode(requested_image.image))
        return StreamingResponse(
            decoded_image,
            headers={
                "Content-Disposition": f"attachment; filename={requested_image.file_name}"
            },
            media_type=requested_image.mime_type,
        )
    raise ItemNotFoundException(message=f"No image found with id {image_id}")
