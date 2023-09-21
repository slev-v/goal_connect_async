from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.schema import UserSchema

from .jwt import create_access_token, get_current_user_from_token
from .models import AuthenticateUser, DeleteUser, ReadUserByUsername, RegisterUser
from .schemas import (
    TokenResponce,
    UserRequest,
    UserResponse,
)

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=UserResponse)
async def get_current_user(
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)]
) -> UserResponse:
    return UserResponse(
        id=current_user.id, email=current_user.email, username=current_user.username
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
    data: UserRequest,
    use_case: RegisterUser = Depends(RegisterUser),
) -> UserResponse:
    user = await use_case.execute(data.email, data.username, data.password)
    return UserResponse(id=user.id, email=user.email, username=user.username)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: Annotated[UserSchema, Depends(get_current_user_from_token)],
    use_case: DeleteUser = Depends(DeleteUser),
) -> None:
    await use_case.execute(current_user.username)


@router.post("/token", response_model=TokenResponce)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: AuthenticateUser = Depends(AuthenticateUser),
) -> TokenResponce:
    user = await use_case.execute(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return TokenResponce(access_token=access_token, token_type="bearer")


@router.delete("/token", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(key="access_token")


@router.get("/{username}", response_model=UserResponse)
async def read(
    username: str,
    use_case: ReadUserByUsername = Depends(ReadUserByUsername),
) -> UserResponse:
    user = await use_case.execute(username)
    return UserResponse(id=user.id, email=user.email, username=user.username)
