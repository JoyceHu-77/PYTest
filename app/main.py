"""
FastAPI 应用入口（与 Docker 的关系）：
- Dockerfile 的 CMD 使用 uvicorn app.main:app，即加载本模块中的变量 app。
- 因此包名必须是 app，且 FastAPI 实例必须命名为 app。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import Base, engine
from app.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时根据模型创建表（开发够用；生产环境常用 Alembic 做迁移）。"""
    import app.models  # noqa: F401 — 注册 ORM 模型到 Base.metadata

    Base.metadata.create_all(bind=engine)
    yield


# FastAPI 应用根对象；标题/描述会出现在自动文档 /docs 中。
app = FastAPI(
    title="iOS App API",
    description="示例后端，供 Swift / iOS 客户端调用",
    version="0.1.0",
    lifespan=lifespan,
)

# 跨域：浏览器或网关场景下需要。开发期 allow_origins=["*"] 省事，上线应改为明确域名列表。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/items", tags=["items"])


# --- 响应模型：定义返回 JSON 的结构（类似 Swift Codable） ---
class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """健康检查，适合在 iOS 里先测「能不能连上服务器」。"""
    return HealthResponse(status="ok", message="server is running")


# --- 示例 POST：请求体 + 响应体 ---
class EchoBody(BaseModel):
    text: str


class EchoResponse(BaseModel):
    echo: str


@app.post("/echo", response_model=EchoResponse)
def echo(body: EchoBody) -> EchoResponse:
    """示例 POST：发送 JSON，返回同样内容（类似 iOS 里 Codable 交互）。"""
    return EchoResponse(echo=body.text)
