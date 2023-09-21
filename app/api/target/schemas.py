from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator


class Target(BaseModel):
    title: str
    target: int
    progress: int

    @model_validator(mode="after")
    def validate_progress(self) -> "Target":
        target = self.target
        progress = self.progress
        if target < progress:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Progress can not be greater than target"
            )
        return self


class TargetRequest(Target):
    pass


class TargetResponse(Target):
    id: int
