from pydantic import BaseModel

from app.api.target.schemas import TargetRequest, TargetResponse
from app.models import GoalSchema


class Goal(BaseModel):
    title: str
    description: str
    private: bool


class GoalRequest(Goal):
    pass


class GoalResponse(Goal):
    id: int
    user_id: int


class GoalWithTargetRequest(GoalRequest):
    targets: list[TargetRequest]


class GoalWithTargetResponse(GoalResponse):
    targets: list[TargetResponse]


class AllGoalsWithTargetResponse(BaseModel):
    goals: list[GoalWithTargetResponse]


class AllGoalsSchemaResponse(BaseModel):
    goals: list[GoalSchema]
