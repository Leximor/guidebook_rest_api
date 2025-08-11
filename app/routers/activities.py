from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.database import get_db
from app.auth import api_key_dependency
from app.services import ActivityService
from app.schemas import ActivityResponse, ActivityTreeResponse, PaginationParams, PaginatedResponse

router = APIRouter(prefix="/api/activities", tags=["Виды деятельности"])


@router.get("/", response_model=PaginatedResponse)
async def get_activities(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список всех видов деятельности с пагинацией
    """
    pagination = PaginationParams(page=page, size=size)
    result = ActivityService.get_activities(db, pagination)
    return PaginatedResponse(**result)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить информацию о виде деятельности по его идентификатору
    """
    activity = ActivityService.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден")

    return activity


@router.get("/tree/", response_model=List[ActivityTreeResponse])
async def get_activity_tree(
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить дерево видов деятельности (только корневые элементы с дочерними)
    """
    activities = ActivityService.get_activity_tree(db)
    return activities
