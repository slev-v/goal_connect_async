from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TargetSchema(BaseModel):
    id: int
    title: str
    target: int
    progress: int
    goal_id: int

    model_config = ConfigDict(from_attributes=True)


class GoalSchema(BaseModel):
    id: int
    title: str
    description: str
    private: bool
    created_at: datetime
    user_id: int
    targets: list[TargetSchema]

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    password: str

    model_config = ConfigDict(from_attributes=True)
