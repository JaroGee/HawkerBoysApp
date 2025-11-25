from __future__ import annotations

import os
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    database_url: str | None = Field(default=os.getenv("DATABASE_URL"))
    admin_password: str = Field(default=os.getenv("ADMIN_PASSWORD", "change-me"))
    logo_path: str = Field(default=os.getenv("HB_LOGO_PATH", "static/assets/images/hb_logo.png"))


settings = Settings()

__all__ = ["settings", "Settings"]
