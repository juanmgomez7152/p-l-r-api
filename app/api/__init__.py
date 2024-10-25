from fastapi import APIRouter

from app.api import translation

router = APIRouter()

router.include_router(translation.router, prefix="/translation")