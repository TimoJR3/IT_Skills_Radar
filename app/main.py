from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Портфельный сервис для анализа спроса на навыки в data и product вакансиях.",
)

app.include_router(router)

