from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.database import Base
import uuid


# Таблица связи организаций и телефонов
organization_phones = Table(
    'organization_phones',
    Base.metadata,
    Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id'), primary_key=True),
    Column('phone', String(20), primary_key=True)
)

# Таблица связи организаций и видов деятельности
organization_activities = Table(
    'organization_activities',
    Base.metadata,
    Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id'), primary_key=True),
    Column('activity_id', UUID(as_uuid=True), ForeignKey('activities.id'), primary_key=True)
)


class Building(Base):
    """Модель здания"""
    __tablename__ = "buildings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(500), nullable=False, unique=True)
    latitude = Column(String(20), nullable=False)
    longitude = Column(String(20), nullable=False)
    coordinates = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

    # Связи
    organizations = relationship("Organization", back_populates="building")

    def __repr__(self):
        return f"<Building(id={self.id}, address='{self.address}')>"


class Activity(Base):
    """Модель вида деятельности"""
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('activities.id'), nullable=True)
    level = Column(Integer, nullable=False, default=1)

    # Ограничение на уровень вложенности
    __table_args__ = (
        CheckConstraint('level <= 3', name='max_level_check'),
    )

    # Связи
    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")
    organizations = relationship("Organization", secondary=organization_activities, back_populates="activities")

    def __repr__(self):
        return f"<Activity(id={self.id}, name='{self.name}', level={self.level})>"


class Organization(Base):
    """Модель организации"""
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False)
    building_id = Column(UUID(as_uuid=True), ForeignKey('buildings.id'), nullable=False)

    # Связи
    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=organization_activities, back_populates="organizations")

    # Свойство для получения телефонов
    @property
    def phones(self):
        """Получить список телефонов организации"""
        from sqlalchemy.orm import object_session
        from sqlalchemy import text
        session = object_session(self)
        if session:
            result = session.execute(
                text("SELECT phone FROM organization_phones WHERE organization_id = :org_id"),
                {"org_id": self.id}
            )
            return [row[0] for row in result]
        return []

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
