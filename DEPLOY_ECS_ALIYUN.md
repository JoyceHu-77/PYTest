# 阿里云 ECS 远程部署（FastAPI + Docker Compose + MySQL 5.7）

面向当前仓库：`api`（FastAPI/Uvicorn）+ `db`（MySQL 5.7），使用 `docker compose` 在 **ECS 上 24 小时运行**。

> 本文不要求你有后端经验；照做即可跑通。命令默认在 **Ubuntu 22.04** 上执行。

---

## 0. 你将得到什么（结果）

- 你的 ECS 公网 IP 能访问：
  - `http://<公网IP>:8000/health`
  - `http://<公网IP>:8000/docs`
- API 可读写数据库（`POST /items/` → MySQL 持久化）。

---

## 1. 购买 ECS（控制台要点）

### 1.1 地域/镜像/规格

- **镜像**：Ubuntu 22.04 64 位
- **规格**：学习用建议 \(2 vCPU / 2GiB\) 起
- **公网**：确保分配公网 IPv4（或绑定 EIP）

### 1.2 安全组（非常关键）

先只放行必要端口：

- **22/TCP**：SSH 登录（建议授权对象先用你的公网 IP/32；测试阶段可临时 0.0.0.0/0）
- **8000/TCP**：对外提供 API（测试阶段可 0.0.0.0/0）

**不要对公网开放 MySQL 3306**（生产更是不要）。

---

## 2. SSH 登录 ECS

你有两种登录方式：**密码** 或 **密钥（.pem）**。

### 2.1 密码登录

在你的 Mac 终端执行（把 IP 换成你的 ECS 公网 IP）：

```bash
ssh root@<公网IP>
```

或（Ubuntu 镜像常见用户）：

```bash
ssh ubuntu@<公网IP>
```

第一次连接会提示确认指纹，输入 **`yes`** 回车。

### 2.2 密钥登录（有 `.pem` 时）

```bash
chmod 400 ~/Downloads/<你的密钥>.pem
ssh -i ~/Downloads/<你的密钥>.pem root@<公网IP>
```

---

## 3. 把项目上传到 ECS（推荐：scp / rsync）

> `scp/rsync` 命令在 **你的 Mac 上执行**，不是在 ECS 里执行。

### 3.1 只上传一次（整目录 scp）

```bash
scp -r /Users/huchenyi/Project/PYTest root@<公网IP>:~/
```

上传后，项目路径通常是：`~/PYTest`。

### 3.2 后续更新（推荐：rsync 增量同步）

```bash
rsync -avz --progress -e ssh \
  --exclude '.venv' --exclude '__pycache__' --exclude '.git' \
  /Users/huchenyi/Project/PYTest/ \
  root@<公网IP>:~/PYTest/
```

---

## 4. 在 ECS 上安装 Docker + Compose

SSH 登录 ECS 后执行：

```bash
apt update
apt install -y ca-certificates curl git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

验证：

```bash
docker --version
docker compose version
```

---

## 5. 配置 Docker 镜像加速（强烈建议）

国内 ECS 直接拉 Docker Hub 常超时或 “not found”。建议用阿里云 **镜像加速器**：

1. 控制台 → **容器镜像服务 ACR** → 镜像加速器，复制你的加速地址（形如 `https://xxxx.mirror.aliyuncs.com`）
2. 在 ECS 上写入：

```bash
mkdir -p /etc/docker

tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://<你的加速地址>.mirror.aliyuncs.com"
  ]
}
EOF

systemctl daemon-reload
systemctl restart docker
```

验证：

```bash
docker info | grep -A5 "Registry Mirrors"
```

---

## 6. 启动服务（docker compose）

### 6.1 设置数据库密码（推荐）

在 ECS 项目目录创建 `.env`（不要提交到 git）：

```bash
cd ~/PYTest
nano .env
```

写一行（示例）：

```text
POSTGRES_PASSWORD=一串足够长的随机密码
```

> 当前 compose 用 `POSTGRES_PASSWORD` 这个变量名复用给 MySQL 密码；仅是变量名，不代表 Postgres。

### 6.2 启动

```bash
cd ~/PYTest
docker compose up --build -d
```

查看状态与日志：

```bash
docker compose ps
docker compose logs -f api
```

---

## 7. 验证是否成功

### 7.1 ECS 本机验证（先排除公网因素）

```bash
curl -s http://127.0.0.1:8000/health
```

期望返回：

```json
{"status":"ok","message":"server is running"}
```

### 7.2 公网验证（从你自己电脑浏览器）

- `http://<公网IP>:8000/health`
- `http://<公网IP>:8000/docs`

若本机通但公网不通，优先检查 **安全组是否放行 8000**。

---

## 8. 常见问题与解决方案（按出现频率排序）

### 8.1 浏览器打不开 `http://<公网IP>:8000/docs`，但 ECS 上 `curl 127.0.0.1:8000/health` 正常

**原因**：安全组未放行 8000 或系统防火墙拦截。

**解决**：
- 控制台安全组入方向添加 **TCP 8000**（测试阶段可 `0.0.0.0/0`）
- ECS 上检查 ufw：
  - `ufw status`
  - 若 active：`ufw allow 8000/tcp && ufw reload`

### 8.2 `docker pull` / `docker compose up` 报 `i/o timeout`、`TLS connection was non-properly terminated`

**原因**：访问 Docker Hub 网络不稳定。

**解决**：配置镜像加速（见第 5 节）；重试 `docker compose pull`。

### 8.3 报 `docker.io/library/<镜像>:<tag>: not found`

**原因 1**：镜像加速器同步不完整（常见于某些 tag/变体）。  
**原因 2**：ECS 上的项目文件没更新，仍在拉旧镜像。

**解决**：
- 先确认 ECS 上 `~/PYTest/docker-compose.yml` 与 `Dockerfile` 是最新：`head -40 docker-compose.yml`、`head -20 Dockerfile`
- 尝试换 tag（例如不使用 `*-alpine` 变体）
- 必要时在网络更好的机器 `docker save` → 上传 → ECS `docker load`

### 8.4 `git clone` 报 `Permission denied (publickey)` 或 `GnuTLS recv error`

**原因**：SSH 密钥未配置 / GitHub 线路不稳定。

**解决**：
- 用 HTTPS + Token，或
- 直接用 `scp/rsync` 上传项目（见第 3 节），不依赖 ECS 访问 GitHub

### 8.5 `POST /items/` 报 500（数据库连不上）

**排查顺序**：

```bash
docker compose ps
docker compose logs --tail 200 db
docker compose logs --tail 200 api
```

**常见原因**：
- `db` 未 healthy（MySQL 初始化慢）→ 等待或调大 `start_period`
- `.env` 修改了密码但容器里仍用旧密码 → `docker compose down` 后再 `up -d`（必要时清理卷）

### 8.6 你改了代码但 ECS 上还是旧行为

**原因**：服务器目录没更新。

**解决**：用 `rsync` 增量同步（第 3.2 节），然后：

```bash
cd ~/PYTest
docker compose up --build -d
```

### 8.7 端口冲突：`port is already allocated`

**原因**：宿主机已有进程占用 8000 或 3306。

**解决**：
- 查占用：`ss -tlnp | grep -E ':(8000|3306)\b'`
- 改 compose 左侧端口，例如把 API 改成 `\"9000:8000\"`（公网访问改用 9000）

---

## 9. 运行与停止（你需要记住的命令）

在 ECS 项目目录下：

```bash
docker compose up --build -d     # 启动/更新
docker compose ps               # 看状态
docker compose logs -f api      # 看日志
docker compose stop             # 停服务（容器还在）
docker compose down             # 停并删除容器（卷默认保留）
```

> **退出 SSH（`exit`）不影响服务运行**；只有 `stop/down` 或关机/停止 ECS 才会让服务不可用。

