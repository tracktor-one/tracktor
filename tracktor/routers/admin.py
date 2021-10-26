import logging
import re
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from fastapi.logger import logger

from tracktor import config
from tracktor.error import ItemNotFoundException, ItemConflictException, ForbiddenException, UnauthorizedException, \
    BadRequestException
from tracktor.models import User, UserResponse, UserCreate, UserUpdate
from tracktor.sql import users
from tracktor.utils.auth import current_user, database, get_user, AdminRequired, get_user_by_entity_id, get_super_admin

PASSWORD_SECURITY = re.compile("((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_\\-/!@#$%^&*\\\\]).{8,30})")
ADMIN_PASSWORD_RESET: Optional[str] = None

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/user", response_model=List[UserResponse], dependencies=[Depends(AdminRequired())])
async def list_all_users():
    return [UserResponse(**x) for x in await database.fetch_all(users.select())]


@router.get("/user/current", response_model=UserResponse, dependencies=[Depends(current_user)])
async def get_current_user(cu: User = Depends(current_user)):
    return UserResponse(**cu.__dict__)


@router.get("/user/{user_id}", response_model=UserResponse, dependencies=[Depends(AdminRequired())])
async def get_single_user(user_id: str):
    if single_user := await get_user_by_entity_id(user_id):
        return UserResponse(**single_user.__dict__)
    raise ItemNotFoundException(message="User not found")


@router.post("/user", response_model=UserResponse, dependencies=[Depends(AdminRequired())])
async def create_user(new_user: UserCreate):
    if await get_user(new_user.name):
        raise ItemConflictException(message="User already exists")
    return await User.create(**new_user.__dict__)


@router.put("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(AdminRequired())])
async def update_user(user_id: str, updated_user: UserUpdate):
    if user := await get_user_by_entity_id(user_id):
        if user.id == 1:
            raise ForbiddenException(message="Operation not permitted")
        return await user.update(**updated_user.__dict__)
    raise ItemNotFoundException(message="User not found")


@router.get("/reset/master")
async def reset_admin_password(token: Optional[str] = None):
    global ADMIN_PASSWORD_RESET
    if not ADMIN_PASSWORD_RESET or not token:
        ADMIN_PASSWORD_RESET = secrets.token_urlsafe(64)
        logger.log(level=logging.WARNING, msg=f"ADMIN PASSWORD RESET TOKEN: {ADMIN_PASSWORD_RESET}")
        return {"message": "A new reset token was generated. Check the logs of this server"}
    if token != ADMIN_PASSWORD_RESET:
        raise UnauthorizedException(message="Invalid reset token")
    admin = await get_super_admin()
    await admin.update(password=config.ADMIN_PASSWORD)
    ADMIN_PASSWORD_RESET = None
    return {"message": f"Admin password is now set to: '{config.ADMIN_PASSWORD}' Change this immediately"}


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(current_user)])
async def change_password(new_password: UserCreate, cu: User = Depends(current_user)):
    if cu.name != new_password.name and not cu.admin:
        raise ForbiddenException(message="Operation not permitted")
    if not PASSWORD_SECURITY.match(new_password.password):
        raise BadRequestException(
            message="The password must have at least 8 characters, including a digit, a lowercase, an uppercase and a special character")
    if user := await get_user(new_password.name):
        return await user.update(password=new_password.password)
    raise ItemNotFoundException(message="User not found")


@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(AdminRequired())])
async def remove_user(user_id: str, cu: User = Depends(current_user)):
    if user_id == cu.entity_id:
        raise ItemConflictException(message="User can not be deleted by same user")

    if delete_user := await get_user_by_entity_id(user_id):
        if delete_user.id == 1:
            raise ItemConflictException(message="Superadmin can not be deleted")
        return await delete_user.delete()
    raise ItemNotFoundException(message="User not found")
