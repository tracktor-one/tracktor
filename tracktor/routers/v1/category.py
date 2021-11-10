"""
V1 of the API - Category
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tracktor.error import ItemNotFoundException
from tracktor.models import CategoryResponse, Category
from tracktor.utils.database import get_session

router = APIRouter(prefix="/category")


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    """
    Request to return all categories
    """
    return [CategoryResponse(**x.__dict__) for x in await Category.get_all(session)]


@router.get("/{category_name}", response_model=List[CategoryResponse])
async def get_category(
    category_name: str, session: AsyncSession = Depends(get_session)
):
    """
    Request to return a category
    """
    if category := await Category.get_by_name(category_name, session):
        return CategoryResponse(**category.__dict__)
    raise ItemNotFoundException(message=f"No category found with name {category_name}")
