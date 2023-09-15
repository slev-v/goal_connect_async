from fastapi import APIRouter

from .goal.router import router as goal_router
from .target.router import router as target_router
from .user.router import router as user_router

router = APIRouter()

router.include_router(user_router)
router.include_router(goal_router)
router.include_router(target_router)
