from pydantic import BaseModel


class Target(BaseModel):
    title: str
    target: int
    progress: int


class TargetRequest(Target):
    pass


class TargetResponse(Target):
    id: int
