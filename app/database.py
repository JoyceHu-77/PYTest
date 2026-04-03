"""
数据库连接与会话。
- Docker 内：compose 注入 DATABASE_URL，主机名用服务名 db（同一 compose 网络内可解析）。
- 本机直接 uvicorn：PostgreSQL 端口映射到本机 5432 时，用默认 URL（localhost）。
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:appsecret@localhost:5432/appdb",
)

# pool_pre_ping：连接池里取出连接前先测活，避免 PostgreSQL 重启后用到坏连接。
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖注入：每个请求一个 Session，结束关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
