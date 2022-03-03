"""
Module for auth router

Contains functions and api endpoints for authentication
"""
from datetime import datetime, timedelta

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import check_password_hash

from tracktor.config import config
from tracktor.error import BadRequestException
from tracktor.models import Token, User
from tracktor.utils.auth import create_token
from tracktor.utils.database import get_session

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """
    Request to login
    """
    if not (await session.execute(select(User))).scalars().all():
        await User.create(
            name=config.ADMIN_USER,
            password=config.ADMIN_PASSWORD,
            admin=True,
            session=session,
        )
    user = await User.get_by_username(form_data.username, session)
    if not user or not check_password_hash(user.password, form_data.password):
        raise BadRequestException(message="Incorrect username or password")
    await user.update(session, last_login=datetime.utcnow())
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user.entity_id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
