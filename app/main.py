from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routers import organizations, buildings, activities
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    REST API приложение для справочника организаций, зданий и видов деятельности.

    ## Функциональность

    ### Организации
    - Получение списка организаций с фильтрацией и пагинацией
    - Поиск организаций по названию
    - Получение организаций в конкретном здании
    - Получение организаций по виду деятельности
    - Получение организаций по дереву видов деятельности
    - Поиск организаций в заданном радиусе или области

    ### Здания
    - Получение списка зданий
    - Получение информации о здании по ID

    ### Виды деятельности
    - Получение списка видов деятельности
    - Получение дерева видов деятельности
    - Получение информации о виде деятельности по ID

    ## Аутентификация

    Все запросы требуют API ключ в заголовке `X-API-Key`.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(activities.router)


@app.get("/", tags=["Корневой эндпоинт"])
async def root():
    """
    Корневой эндпоинт с информацией о приложении
    """
    return {
        "message": "Guidebook REST API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Здоровье"])
async def health_check():
    """
    Проверка здоровья приложения
    """
    return {"status": "healthy", "version": settings.app_version}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Обработчик HTTP исключений
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Обработчик общих исключений
    """
    logger.error(f"Необработанное исключение: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
