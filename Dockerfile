# =============================================================================
# Dockerfile：定义「如何构建 Docker 镜像」（只读模板）。构建命令示例：docker build -t 名字 .
# 镜像 vs 容器：镜像是模板；docker run / compose up 用镜像启动的才是容器（运行中的实例）。
# =============================================================================

# 基础镜像：官方 Python 3.12；slim 体积小，一般 Web 服务够用。
FROM python:3.12-slim

# 容器内工作目录；后续 COPY、RUN、CMD 的相对路径都相对于此（类似 cd /app）。
WORKDIR /app

# PYTHONDONTWRITEBYTECODE=1：不生成 .pyc，镜像更干净。
# PYTHONUNBUFFERED=1：日志不缓冲，docker logs 能立刻看到 print/日志。
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 先只复制依赖清单再 pip：业务代码变更时 Docker 可复用「已安装依赖」这一层，构建更快。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制应用代码到 /app/app/，保证 Python 包名为 app，与 uvicorn app.main:app 一致。
COPY app ./app

# 声明容器内进程打算使用的端口（文档/约定）；真正映射到 Mac 要靠 compose 的 ports 或 docker run -p。
EXPOSE 8000

# 容器启动时默认执行的命令（exec 形式，PID 1 为 uvicorn）。
# app.main:app = 模块 app.main 中的变量 app（FastAPI 实例）。
# --host 0.0.0.0：在容器内监听所有网卡；若只写 127.0.0.1，宿主机无法通过端口映射访问。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
