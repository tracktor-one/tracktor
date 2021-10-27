"""
Module for admin router

Contains functions and api endpoints for user management
"""
import logging
import re
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from fastapi.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tracktor.config import config
from tracktor.error import ItemNotFoundException, ItemConflictException, \
    ForbiddenException, UnauthorizedException, \
    BadRequestException
from tracktor.models import User, UserResponse, UserCreate, UserUpdate
from tracktor.utils.auth import current_user, get_user, admin_required, \
    get_user_by_entity_id, get_super_admin
from tracktor.utils.database import get_session

PASSWORD_SECURITY = re.compile("((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_\\-/!@#$%^&*\\\\]).{8,30})")
ADMIN_PASSWORD_RESET: Optional[str] = None

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/user", response_model=List[UserResponse], dependencies=[Depends(admin_required)])
async def list_all_users(session: AsyncSession = Depends(get_session)):
    """
    Request to list all users
    """
    return [UserResponse(**x.__dict__)
            for x in (await session.execute(select(User))).scalars().all()]


@router.get("/user/current", response_model=UserResponse, dependencies=[Depends(current_user)])
async def get_current_user(request_user: User = Depends(current_user)):
    """
    Request to return the current user
    """
    return UserResponse(**request_user.__dict__)


@router.get("/user/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)])
async def get_single_user(user_id: str, session: AsyncSession = Depends(get_session)):
    """
    Request to return a single user
    """
    if single_user := await get_user_by_entity_id(user_id, session):
        return UserResponse(**single_user.__dict__)
    raise ItemNotFoundException(message="User not found")


@router.post("/user", response_model=UserResponse, dependencies=[Depends(admin_required)])
async def create_user(new_user: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Request to create a user
    """
    if await get_user(new_user.name, session):
        raise ItemConflictException(message="User already exists")
    return await User.create(session, **new_user.__dict__)


@router.put("/user/{user_id}",
            response_model=UserResponse,
            dependencies=[Depends(admin_required)])
async def update_user(user_id: str, updated_user: UserUpdate,
                      session: AsyncSession = Depends(get_session)):
    """
    Request to update a given user
    """
    if user := await get_user_by_entity_id(user_id, session):
        if user.id == 1:
            raise ForbiddenException(message="Operation not permitted")
        return UserResponse(**(await user.update(session, **updated_user.__dict__)).__dict__)
    raise ItemNotFoundException(message="User not found")


@router.get("/reset/master")
async def reset_admin_password(token: Optional[str] = None,
                               session: AsyncSession = Depends(get_session)):
    """
    Request to reset the admin password
    """
    global ADMIN_PASSWORD_RESET  # pylint: disable=global-statement
    if not ADMIN_PASSWORD_RESET or not token:
        ADMIN_PASSWORD_RESET = secrets.token_urlsafe(64)
        logger.log(level=logging.WARNING, msg=f"ADMIN PASSWORD RESET TOKEN: {ADMIN_PASSWORD_RESET}")
        return {"message": "A new reset token was generated. Check the logs of this server"}
    if token != ADMIN_PASSWORD_RESET:
        ADMIN_PASSWORD_RESET = secrets.token_urlsafe(64)
        logger.log(level=logging.WARNING, msg=f"ADMIN PASSWORD RESET TOKEN: {ADMIN_PASSWORD_RESET}")
        raise UnauthorizedException(message="Invalid reset token. A new token has been generated")
    admin = await get_super_admin(session)
    await admin.update(password=config.ADMIN_PASSWORD)
    ADMIN_PASSWORD_RESET = None
    return {
        "message":
            f"Admin password is now set to: '{config.ADMIN_PASSWORD}' Change this immediately"
    }


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(current_user)])
async def change_password(new_password: UserCreate, request_user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_session)):
    """
    Request to change the password of a given user
    """
    if request_user.name != new_password.name and not request_user.admin:
        raise ForbiddenException(message="Operation not permitted")
    if not PASSWORD_SECURITY.match(new_password.password):
        raise BadRequestException(
            message="The password must have at least 8 characters," +
                    " including a digit, a lowercase, an uppercase and a special character")
    if user := await get_user(new_password.name, session):
        return await user.update(session, password=new_password.password)
    raise ItemNotFoundException(message="User not found")


@router.delete("/user/{user_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(admin_required)])
async def remove_user(user_id: str, request_user: User = Depends(current_user),
                      session: AsyncSession = Depends(get_session)):
    """
    Request to remove a given user from database
    """
    if user_id == request_user.entity_id:
        raise ItemConflictException(message="User can not be deleted by same user")

    delete_user = await get_user_by_entity_id(user_id, session)
    if not delete_user:
        raise ItemNotFoundException(message="User not found")
    if delete_user.id == 1:
        raise ItemConflictException(message="Superadmin can not be deleted")
    await delete_user.delete(session)
