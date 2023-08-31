from fastapi import APIRouter

from .user.router import router as user_router
from .goal.router import router as goal_router

router = APIRouter()

router.include_router(user_router)
router.include_router(goal_router)
