from fastapi import HTTPException, Depends, Header
from typing import Optional
from app.config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """
    Проверка API ключа

    Args:
        x_api_key: API ключ из заголовка X-API-Key

    Returns:
        bool: True если ключ верный

    Raises:
        HTTPException: Если ключ отсутствует или неверный
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API ключ обязателен. Добавьте заголовок X-API-Key"
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Неверный API ключ"
        )

    return True


# Dependency для использования в эндпоинтах
api_key_dependency = Depends(verify_api_key)
