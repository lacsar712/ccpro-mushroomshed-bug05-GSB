import os
from datetime import timedelta


class Config:
    database_url: str = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://mushroomshed:mushroomshed@localhost:3310/mushroomshed",
    )
    jwt_secret: str = os.environ.get("JWT_SECRET", "mushroom-shed-jwt-secret-change-me")
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    @property
    def jwt_access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)


settings = Config()
