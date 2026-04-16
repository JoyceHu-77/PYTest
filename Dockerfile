# =============================================================================
# Dockerfile：定义「如何构建 Docker 镜像」（只读模板）。构建命令示例：docker build -t 名字 .
# 镜像 vs 容器：镜像是模板；docker run / compose up 用镜像启动的才是容器（运行中的实例）。
# =============================================================================

# 不直接使用 docker.io/library/python:*：国内部分镜像加速对「python 官方库」manifest 常报 not found。
# 改用 Ubuntu 基础镜像 + apt/venv，仅依赖 ubuntu（一般更易被镜像站缓存）。
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# 先只复制依赖清单再 pip：业务代码变更时 Docker 可复用「已安装依赖」这一层，构建更快。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制应用代码到 /app/app/，保证 Python 包名为 app，与 uvicorn app.main:app 一致。
COPY app ./app

# 声明容器内进程打算使用的端口（文档/约定）；真正映射到宿主机要靠 compose 的 ports 或 docker run -p。
EXPOSE 8000

# app.main:app = 模块 app.main 中的变量 app（FastAPI 实例）。
# --host 0.0.0.0：在容器内监听所有网卡；若只写 127.0.0.1，宿主机无法通过端口映射访问。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
