from fastapi import FastAPI

from app.api.main import router

app = FastAPI()

app.include_router(router)


@app.get("/", include_in_schema=False)
async def health() -> dict:
    return {"message": "it's working"}
