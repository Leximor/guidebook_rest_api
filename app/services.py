from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, text
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.models import Organization, Building, Activity
from app.schemas import OrganizationSearchParams, PaginationParams
import logging

logger = logging.getLogger(__name__)


class OrganizationService:
    """Сервис для работы с организациями"""

    @staticmethod
    def get_organizations(
        db: Session,
        pagination: PaginationParams,
        search_params: Optional[OrganizationSearchParams] = None
    ) -> Dict[str, Any]:
        """Получить список организаций с фильтрацией и пагинацией"""

        query = db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        )

        # Применяем фильтры
        if search_params:
            query = OrganizationService._apply_filters(query, search_params)

        # Подсчитываем общее количество
        total = query.count()

        # Применяем пагинацию
        organizations = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": organizations,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_organization_by_id(db: Session, org_id: UUID) -> Optional[Organization]:
        """Получить организацию по ID"""
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).filter(Organization.id == org_id).first()

    @staticmethod
    def search_organizations_by_name(db: Session, name: str, pagination: PaginationParams) -> Dict[str, Any]:
        """Поиск организаций по названию"""
        query = db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).filter(Organization.name.ilike(f"%{name}%"))

        total = query.count()
        organizations = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": organizations,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_organizations_by_building(db: Session, building_id: UUID, pagination: PaginationParams) -> Dict[str, Any]:
        """Получить организации в конкретном здании"""
        query = db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).filter(Organization.building_id == building_id)

        total = query.count()
        organizations = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": organizations,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_organizations_by_activity(db: Session, activity_id: UUID, pagination: PaginationParams) -> Dict[str, Any]:
        """Получить организации по виду деятельности"""
        query = db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).join(Organization.activities).filter(Activity.id == activity_id)

        total = query.count()
        organizations = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": organizations,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_organizations_by_activity_tree(db: Session, activity_id: UUID, pagination: PaginationParams) -> Dict[str, Any]:
        """Получить организации по дереву видов деятельности"""
        # Получаем все дочерние виды деятельности
        activity_ids = OrganizationService._get_activity_tree_ids(db, activity_id)
        activity_ids.append(activity_id)  # Добавляем сам родительский вид деятельности

        query = db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        ).join(Organization.activities).filter(Activity.id.in_(activity_ids))

        total = query.count()
        organizations = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": organizations,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_organizations_nearby(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        pagination: PaginationParams = PaginationParams()
    ) -> Dict[str, Any]:
        """Получить организации в заданном радиусе или прямоугольной области"""

        if radius_km:
            # Поиск в радиусе
            query = db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.activities)
            ).join(Organization.building).filter(
                func.ST_DWithin(
                    Building.coordinates,
                    func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326),
                    radius_km * 1000  # Конвертируем в метры
                )
            )
        else:
            # Поиск в прямоугольной области
            query = db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.activities)
            ).join(Organization.building).filter(
                and_(
                    text("CAST(buildings.latitude AS NUMERIC) >= :min_lat"),
                    text("CAST(buildings.latitude AS NUMERIC) <= :max_lat"),
                    text("CAST(buildings.longitude AS NUMERIC) >= :min_lon"),
                    text("CAST(buildings.longitude AS NUMERIC) <= :max_lon")
                )
            ).params(
                min_lat=min_lat,
                max_lat=max_lat,
                min_lon=min_lon,
                max_lon=max_lon
            )

        total = query.count()
        organizations = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": organizations,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def _apply_filters(query, search_params: OrganizationSearchParams):
        """Применить фильтры к запросу"""
        if search_params.name:
            query = query.filter(Organization.name.ilike(f"%{search_params.name}%"))

        if search_params.building_id:
            query = query.filter(Organization.building_id == search_params.building_id)

        if search_params.activity_id:
            query = query.join(Organization.activities).filter(Activity.id == search_params.activity_id)

        if search_params.activity_tree_id:
            # Получаем сессию из query
            db = query.session
            activity_ids = OrganizationService._get_activity_tree_ids(db, search_params.activity_tree_id)
            activity_ids.append(search_params.activity_tree_id)
            query = query.join(Organization.activities).filter(Activity.id.in_(activity_ids))

        return query

    @staticmethod
    def _get_activity_tree_ids(db: Session, activity_id: UUID) -> List[UUID]:
        """Получить все ID дочерних видов деятельности"""
        activity_ids = []

        def get_children(parent_id: UUID):
            children = db.query(Activity).filter(Activity.parent_id == parent_id).all()
            for child in children:
                activity_ids.append(child.id)
                get_children(child.id)

        get_children(activity_id)
        return activity_ids


class BuildingService:
    """Сервис для работы со зданиями"""

    @staticmethod
    def get_buildings(db: Session, pagination: PaginationParams) -> Dict[str, Any]:
        """Получить список зданий"""
        query = db.query(Building)

        total = query.count()
        buildings = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": buildings,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_building_by_id(db: Session, building_id: UUID) -> Optional[Building]:
        """Получить здание по ID"""
        return db.query(Building).filter(Building.id == building_id).first()


class ActivityService:
    """Сервис для работы с видами деятельности"""

    @staticmethod
    def get_activities(db: Session, pagination: PaginationParams) -> Dict[str, Any]:
        """Получить список видов деятельности"""
        query = db.query(Activity).options(joinedload(Activity.children))

        total = query.count()
        activities = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

        pages = (total + pagination.size - 1) // pagination.size
        return {
            "items": activities,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": pages
        }

    @staticmethod
    def get_activity_by_id(db: Session, activity_id: UUID) -> Optional[Activity]:
        """Получить вид деятельности по ID"""
        return db.query(Activity).options(joinedload(Activity.children)).filter(Activity.id == activity_id).first()

    @staticmethod
    def get_activity_tree(db: Session) -> List[Activity]:
        """Получить дерево видов деятельности"""
        return db.query(Activity).options(joinedload(Activity.children)).filter(Activity.parent_id.is_(None)).all()
