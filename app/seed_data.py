#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import Building, Activity, Organization
from app.config import settings
import uuid

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_test_data():
    """Создание тестовых данных"""
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже данные
        try:
            if db.query(Building).count() > 0:
                print("База данных уже содержит данные. Пропускаем заполнение.")
                return
        except Exception as e:
            # Таблицы еще не созданы, продолжаем
            print(f"Таблицы еще не созданы: {e}")
            return

        print("Создание тестовых данных...")

        # Создаем здания
        buildings = [
            Building(
                id=uuid.uuid4(),
                address="г. Москва, ул. Ленина 1, офис 3",
                latitude="55.7558",
                longitude="37.6176",
                coordinates="POINT(37.6176 55.7558)"
            ),
            Building(
                id=uuid.uuid4(),
                address="г. Москва, ул. Тверская 10, офис 5",
                latitude="55.7576",
                longitude="37.6136",
                coordinates="POINT(37.6136 55.7576)"
            ),
            Building(
                id=uuid.uuid4(),
                address="г. Москва, ул. Арбат 20",
                latitude="55.7494",
                longitude="37.5916",
                coordinates="POINT(37.5916 55.7494)"
            ),
            Building(
                id=uuid.uuid4(),
                address="г. Москва, ул. Блюхера 32/1",
                latitude="55.7600",
                longitude="37.6400",
                coordinates="POINT(37.6400 55.7600)"
            ),
            Building(
                id=uuid.uuid4(),
                address="г. Москва, ул. Новый Арбат 15",
                latitude="55.7500",
                longitude="37.5800",
                coordinates="POINT(37.5800 55.7500)"
            )
        ]

        for building in buildings:
            db.add(building)

        db.commit()
        print(f"Создано {len(buildings)} зданий")

        # Создаем виды деятельности (иерархическая структура)
        activities = []

        # Уровень 1
        food_activity = Activity(
            id=uuid.uuid4(),
            name="Еда",
            parent_id=None,
            level=1
        )
        activities.append(food_activity)

        cars_activity = Activity(
            id=uuid.uuid4(),
            name="Автомобили",
            parent_id=None,
            level=1
        )
        activities.append(cars_activity)

        services_activity = Activity(
            id=uuid.uuid4(),
            name="Услуги",
            parent_id=None,
            level=1
        )
        activities.append(services_activity)

        db.commit()

        # Уровень 2
        meat_activity = Activity(
            id=uuid.uuid4(),
            name="Мясная продукция",
            parent_id=food_activity.id,
            level=2
        )
        activities.append(meat_activity)

        dairy_activity = Activity(
            id=uuid.uuid4(),
            name="Молочная продукция",
            parent_id=food_activity.id,
            level=2
        )
        activities.append(dairy_activity)

        bread_activity = Activity(
            id=uuid.uuid4(),
            name="Хлебобулочные изделия",
            parent_id=food_activity.id,
            level=2
        )
        activities.append(bread_activity)

        cargo_cars_activity = Activity(
            id=uuid.uuid4(),
            name="Грузовые",
            parent_id=cars_activity.id,
            level=2
        )
        activities.append(cargo_cars_activity)

        passenger_cars_activity = Activity(
            id=uuid.uuid4(),
            name="Легковые",
            parent_id=cars_activity.id,
            level=2
        )
        activities.append(passenger_cars_activity)

        repair_activity = Activity(
            id=uuid.uuid4(),
            name="Ремонт",
            parent_id=services_activity.id,
            level=2
        )
        activities.append(repair_activity)

        db.commit()

        # Уровень 3
        parts_activity = Activity(
            id=uuid.uuid4(),
            name="Запчасти",
            parent_id=passenger_cars_activity.id,
            level=3
        )
        activities.append(parts_activity)

        accessories_activity = Activity(
            id=uuid.uuid4(),
            name="Аксессуары",
            parent_id=passenger_cars_activity.id,
            level=3
        )
        activities.append(accessories_activity)

        for activity in activities:
            db.add(activity)

        db.commit()
        print(f"Создано {len(activities)} видов деятельности")

        # Создаем организации
        organizations = [
            Organization(
                id=uuid.uuid4(),
                name='ООО "Рога и Копыта"',
                building_id=buildings[0].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ИП "Молочная ферма"',
                building_id=buildings[1].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ООО "Мясной двор"',
                building_id=buildings[2].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ООО "Автосервис"',
                building_id=buildings[3].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ИП "Хлеб и калачи"',
                building_id=buildings[4].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ООО "Автозапчасти"',
                building_id=buildings[0].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ООО "Автоаксессуары"',
                building_id=buildings[1].id
            ),
            Organization(
                id=uuid.uuid4(),
                name='ООО "Грузоперевозки"',
                building_id=buildings[2].id
            )
        ]

        for org in organizations:
            db.add(org)

        db.commit()
        print(f"Создано {len(organizations)} организаций")

        # Добавляем телефоны к организациям
        phone_data = [
            (organizations[0].id, ["2-222-222", "3-333-333", "8-923-666-13-13"]),
            (organizations[1].id, ["4-444-444", "5-555-555"]),
            (organizations[2].id, ["6-666-666"]),
            (organizations[3].id, ["7-777-777", "8-888-888"]),
            (organizations[4].id, ["9-999-999"]),
            (organizations[5].id, ["1-111-111"]),
            (organizations[6].id, ["2-333-444"]),
            (organizations[7].id, ["5-666-777"])
        ]

        for org_id, phones in phone_data:
            for phone in phones:
                db.execute(
                    text("INSERT INTO organization_phones (organization_id, phone) VALUES (:org_id, :phone)"),
                    {"org_id": org_id, "phone": phone}
                )

        # Добавляем связи организаций с видами деятельности
        activity_relations = [
            (organizations[0].id, [meat_activity.id, dairy_activity.id]),  # Рога и Копыта - мясо и молоко
            (organizations[1].id, [dairy_activity.id]),  # Молочная ферма - только молоко
            (organizations[2].id, [meat_activity.id]),  # Мясной двор - только мясо
            (organizations[3].id, [repair_activity.id]),  # Автосервис - ремонт
            (organizations[4].id, [bread_activity.id]),  # Хлеб и калачи - хлеб
            (organizations[5].id, [parts_activity.id]),  # Автозапчасти - запчасти
            (organizations[6].id, [accessories_activity.id]),  # Автоаксессуары - аксессуары
            (organizations[7].id, [cargo_cars_activity.id])  # Грузоперевозки - грузовые
        ]

        for org_id, activity_ids in activity_relations:
            for activity_id in activity_ids:
                db.execute(
                    text("INSERT INTO organization_activities (organization_id, activity_id) VALUES (:org_id, :activity_id)"),
                    {"org_id": org_id, "activity_id": activity_id}
                )

        db.commit()
        print("Тестовые данные успешно созданы!")

    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
