from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.auth import api_key_dependency
from app.services import OrganizationService
from app.schemas import (
    OrganizationResponse, PaginationParams, OrganizationSearchParams,
    PaginatedResponse
)

router = APIRouter(prefix="/api/organizations", tags=["Организации"])


@router.get("/", response_model=PaginatedResponse)
async def get_organizations(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    building_id: Optional[UUID] = Query(None, description="Фильтр по ID здания"),
    activity_id: Optional[UUID] = Query(None, description="Фильтр по ID вида деятельности"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список всех организаций с возможностью фильтрации и пагинации
    """
    pagination = PaginationParams(page=page, size=size)
    search_params = OrganizationSearchParams(
        name=name,
        building_id=building_id,
        activity_id=activity_id
    )

    result = OrganizationService.get_organizations(db, pagination, search_params)
    return PaginatedResponse(**result)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить информацию об организации по её идентификатору
    """
    organization = OrganizationService.get_organization_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    return organization


@router.get("/search/", response_model=PaginatedResponse)
async def search_organizations_by_name(
    name: str = Query(..., description="Название организации для поиска"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Поиск организаций по названию
    """
    pagination = PaginationParams(page=page, size=size)
    result = OrganizationService.search_organizations_by_name(db, name, pagination)
    return PaginatedResponse(**result)


@router.get("/by-building/{building_id}", response_model=PaginatedResponse)
async def get_organizations_by_building(
    building_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список всех организаций, находящихся в конкретном здании
    """
    pagination = PaginationParams(page=page, size=size)
    result = OrganizationService.get_organizations_by_building(db, building_id, pagination)
    return PaginatedResponse(**result)


@router.get("/by-activity/{activity_id}", response_model=PaginatedResponse)
async def get_organizations_by_activity(
    activity_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список всех организаций, которые относятся к указанному виду деятельности
    """
    pagination = PaginationParams(page=page, size=size)
    result = OrganizationService.get_organizations_by_activity(db, activity_id, pagination)
    return PaginatedResponse(**result)


@router.get("/by-activity-tree/{activity_id}", response_model=PaginatedResponse)
async def get_organizations_by_activity_tree(
    activity_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список организаций по дереву видов деятельности.
    Включает организации с указанным видом деятельности и всеми его дочерними видами.
    """
    pagination = PaginationParams(page=page, size=size)
    result = OrganizationService.get_organizations_by_activity_tree(db, activity_id, pagination)
    return PaginatedResponse(**result)


@router.get("/nearby/", response_model=PaginatedResponse)
async def get_organizations_nearby(
    latitude: float = Query(..., description="Широта центра поиска"),
    longitude: float = Query(..., description="Долгота центра поиска"),
    radius_km: Optional[float] = Query(None, description="Радиус поиска в километрах"),
    min_lat: Optional[float] = Query(None, description="Минимальная широта для прямоугольной области"),
    max_lat: Optional[float] = Query(None, description="Максимальная широта для прямоугольной области"),
    min_lon: Optional[float] = Query(None, description="Минимальная долгота для прямоугольной области"),
    max_lon: Optional[float] = Query(None, description="Максимальная долгота для прямоугольной области"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
    _: bool = api_key_dependency
):
    """
    Получить список организаций, которые находятся в заданном радиусе или прямоугольной области
    относительно указанной точки на карте.

    Используйте либо radius_km для поиска в радиусе, либо min_lat/max_lat/min_lon/max_lon для поиска в прямоугольной области.
    """
    if radius_km is None and (min_lat is None or max_lat is None or min_lon is None or max_lon is None):
        raise HTTPException(
            status_code=400,
            detail="Необходимо указать либо radius_km, либо все параметры прямоугольной области (min_lat, max_lat, min_lon, max_lon)"
        )

    pagination = PaginationParams(page=page, size=size)
    result = OrganizationService.get_organizations_nearby(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        pagination=pagination
    )
    return PaginatedResponse(**result)
