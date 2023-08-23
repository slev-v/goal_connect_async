from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TargetSchema(BaseModel):
    id: int
    title: str
    target: int
    goal_id: int

    model_config = ConfigDict(from_attributes=True)


class GoalSchema(BaseModel):
    id: int
    title: str
    description: str
    private: bool
    created_at: datetime
    targets: list[TargetSchema]
    creator: int

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    password: str
    # goals: list[GoalSchema]

    model_config = ConfigDict(from_attributes=True)
