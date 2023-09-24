from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int
    JWT_ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
