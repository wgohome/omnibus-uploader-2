# For old uploader_wip
# To be deprecated

from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    # MongoDB URL and database name
    DATABASE_URL: str
    DATABASE_NAME: str

    # Directory path
    DATA_DIR: str
    LOG_DIR: str
    GENE_LABEL_MAPPING_DIR: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("DATA_DIR", "LOG_DIR", "GENE_LABEL_MAPPING_DIR")
    def set_path_with_trailing_slash(cls, v):
        if v.endswith("/"):
            return v
        return v + "/"


settings = Settings()  # type: ignore

__all__ = ["settings"]
