from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # MongoDB URL and database name
    DATABASE_URL: str
    DATABASE_NAME: str
    TEST_DATABASE_NAME: str = ""

    # Directory path
    DATA_DIR: str
    LOG_DIR: str
    TEST_DATA_DIR: str = "tests/data/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("DATA_DIR", "LOG_DIR", "TEST_DATA_DIR")
    def set_path_with_trailing_slash(cls, v):
        if v.endswith("/"):
            return v
        return v + "/"

    @validator("TEST_DATABASE_NAME")
    def set_test_database_name(cls, v, values):
        if v:
            return v
        return f"test_{values['DATABASE_NAME']}"


settings = Settings()  # type: ignore

__all__ = ["settings"]
