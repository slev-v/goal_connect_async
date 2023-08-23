from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from app.config import settings
from .utils import OAuth2PasswordBearerWithCookie
from .model import ReadUserByUsername


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/user/token")
optional_oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="/user/token", auto_error=False
)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def optional_get_current_user_from_token(
    token: str = Depends(optional_oauth2_scheme),
):
    if not token:
        return None

    return await get_current_user_from_token(token)


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    use_case: ReadUserByUsername = Depends(ReadUserByUsername),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await use_case.execute(username)
    if user is None:
        raise credentials_exception
    return user
