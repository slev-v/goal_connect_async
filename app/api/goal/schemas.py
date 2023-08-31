from typing import List

from pydantic import BaseModel, Field

from app.models import GoalSchema


class Goal(BaseModel):
    title: str
    description: str
    private: bool


class GoalRequest(Goal):
    pass


class GoalResponse(Goal):
    id: int


class Target(BaseModel):
    title: str
    target: int


class TargetRequest(Target):
    pass


class TargetResponse(Target):
    id: int


class GoalWithTargetRequest(GoalRequest):
    targets: list[TargetRequest]


class GoalWithTargetResponse(GoalResponse):
    targets: list[TargetResponse]


class AllGoalsWithTargetResponse(BaseModel):
    goals: list[GoalWithTargetResponse]


class AllGoalsSchemaResponse(BaseModel):
    goals: list[GoalSchema]


#
#
# class ReadUserGoalsResponse(BaseModel):
#     goals: list[GoalSchema]
#
#
# class AddTargetRequest(BaseModel):
#     title: str
#     target: int
#
#
# class UpdateTargetRequest(AddTargetRequest):
#     pass
