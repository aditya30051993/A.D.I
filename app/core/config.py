from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    debug: bool = True

settings = Settings()
