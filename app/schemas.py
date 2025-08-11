from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime


class BuildingBase(BaseModel):
    """Базовая схема здания"""
    address: str = Field(..., description="Адрес здания", example="г. Москва, ул. Ленина 1, офис 3")
    latitude: str = Field(..., description="Широта", example="55.7558")
    longitude: str = Field(..., description="Долгота", example="37.6176")


class BuildingCreate(BuildingBase):
    """Схема для создания здания"""
    pass


class BuildingResponse(BuildingBase):
    """Схема ответа для здания"""
    id: UUID
    coordinates: str = Field(..., description="Географические координаты в формате WKT")

    @validator('coordinates', pre=True)
    def convert_coordinates(cls, v):
        if hasattr(v, 'desc'):
            return v.desc
        return str(v)

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    """Базовая схема вида деятельности"""
    name: str = Field(..., description="Название вида деятельности", example="Молочная продукция")
    parent_id: Optional[UUID] = Field(None, description="ID родительского вида деятельности")
    level: int = Field(1, description="Уровень вложенности", ge=1, le=3)


class ActivityCreate(ActivityBase):
    """Схема для создания вида деятельности"""
    pass


class ActivityResponse(ActivityBase):
    """Схема ответа для вида деятельности"""
    id: UUID
    children: List['ActivityResponse'] = []

    class Config:
        from_attributes = True


class ActivityTreeResponse(BaseModel):
    """Схема для дерева видов деятельности"""
    id: UUID
    name: str
    level: int
    children: List['ActivityTreeResponse'] = []

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    """Базовая схема организации"""
    name: str = Field(..., description="Название организации", example='ООО "Рога и Копыта"')
    building_id: UUID = Field(..., description="ID здания")
    phones: List[str] = Field(..., description="Список телефонов", example=["2-222-222", "3-333-333"])
    activity_ids: List[UUID] = Field(..., description="Список ID видов деятельности")


class OrganizationCreate(OrganizationBase):
    """Схема для создания организации"""
    pass


class OrganizationResponse(BaseModel):
    """Схема ответа для организации"""
    id: UUID
    name: str
    phones: List[str]
    building: BuildingResponse
    activities: List[ActivityResponse]

    class Config:
        from_attributes = True


class OrganizationSearchParams(BaseModel):
    """Параметры поиска организаций"""
    name: Optional[str] = Field(None, description="Название организации для поиска")
    building_id: Optional[UUID] = Field(None, description="ID здания")
    activity_id: Optional[UUID] = Field(None, description="ID вида деятельности")
    activity_tree_id: Optional[UUID] = Field(None, description="ID вида деятельности для поиска по дереву")

    # Параметры для поиска по географии
    latitude: Optional[float] = Field(None, description="Широта центра поиска")
    longitude: Optional[float] = Field(None, description="Долгота центра поиска")
    radius_km: Optional[float] = Field(None, description="Радиус поиска в километрах")

    # Параметры для поиска в прямоугольной области
    min_lat: Optional[float] = Field(None, description="Минимальная широта")
    max_lat: Optional[float] = Field(None, description="Максимальная широта")
    min_lon: Optional[float] = Field(None, description="Минимальная долгота")
    max_lon: Optional[float] = Field(None, description="Максимальная долгота")

    @validator('radius_km')
    def validate_radius(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Радиус должен быть положительным числом')
        return v


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(1, description="Номер страницы", ge=1)
    size: int = Field(20, description="Размер страницы", ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Схема для пагинированного ответа"""
    items: List[Union[OrganizationResponse, BuildingResponse, ActivityResponse]]
    total: int
    page: int
    size: int
    pages: int

    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        if 'total' in values and 'size' in values:
            return (values['total'] + values['size'] - 1) // values['size']
        return v


# Обновляем forward references
ActivityResponse.model_rebuild()
ActivityTreeResponse.model_rebuild()
