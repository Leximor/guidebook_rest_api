from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.auth import api_key_dependency
from app.services import BuildingService
from app.schemas import BuildingResponse, PaginationParams, PaginatedResponse

router = APIRouter(prefix="/api/buildings", tags=["Здания"])


@router.get("/", response_model=PaginatedResponse)
async def get_buildings(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список всех зданий с пагинацией
    """
    pagination = PaginationParams(page=page, size=size)
    result = BuildingService.get_buildings(db, pagination)
    return PaginatedResponse(**result)


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: UUID,
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить информацию о здании по его идентификатору
    """
    building = BuildingService.get_building_by_id(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Здание не найдено")

    return building
