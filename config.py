from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_NAME: str
    DATA_DIR: str
    LOG_DIR: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("DATA_DIR", "LOG_DIR")
    def set_path_with_trailing_slash(cls, v):
        if v.endswith("/"):
            return v
        return v + "/"


settings = Settings()  # type: ignore

__all__ = ["settings"]
