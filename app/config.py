from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    JWT_SECRET: str
    JWT_EXPIRE_MINUTE: int
    JWT_ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
