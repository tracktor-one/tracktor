from datetime import datetime, timedelta

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from tracktor import config
from tracktor.error import BadRequestException
from tracktor.models import Token
from tracktor.utils.auth import get_user, create_token
from werkzeug.security import check_password_hash

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not check_password_hash(user.password, form_data.password):
        raise BadRequestException(message="Incorrect username or password")
    await user.update(last_login=datetime.utcnow())
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user.entity_id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
