# FastAPI + Docker + PostgreSQL：从零到跑通（零基础版）

**适合谁读**：从未写过后端、但会用电脑和浏览器的大学生。读完并跟做，应能：**在本机用 Docker 同时跑起 API 和数据库**、**在网页里调用接口**、**理解各文件大致分工**，并能用 **TablePlus** 看到表里的数据。

**预计时间**：第一次跟做约 **40～90 分钟**（含下载 Docker 镜像）。

**本文假设**：你已经拿到本教程所在的**整个项目文件夹**（含 `app/`、`docker-compose.yml` 等）。文件内容已在仓库里写好；你要做的是**安装工具、执行命令、理解含义**。若老师只给了压缩包，解压后记住该文件夹路径即可。

---

## 建议怎么读（避免迷路）

| 如果你… | 建议 |
|--------|------|
| 只想尽快看到效果 | 先看 [快速路线：最少步骤跑通](#快速路线最少步骤跑通)，再按需回头补概念。 |
| 想搞懂「为什么」 | 按目录顺序读，重点看 [零基础概念速览](#零基础概念速览) 和 [请求是怎样到达数据库的](#请求是怎样到达数据库的)。 |
| 做某一步报错了 | 直接查 [常见问题排查](#常见问题排查)。 |

---

## 目录

1. [快速路线：最少步骤跑通](#快速路线最少步骤跑通)
2. [零基础概念速览](#零基础概念速览)
3. [开始前：你要安装什么](#开始前你要安装什么)
4. [构建 Python 环境（可选，但建议做）](#4-构建-python-环境可选但建议做)
5. [理解项目里的 Docker 相关文件](#5-理解项目里的-docker-相关文件)
6. [用一条命令起 API + 数据库](#6-用一条命令起-api--数据库)
7. [起服务之后：Python 代码各自干什么](#7-起服务之后python-代码各自干什么)
8. [数据库与增删改查（CRUD）](#8-数据库与增删改查crud)
9. [如何验证是否成功](#9-如何验证是否成功)
10. [用 TablePlus 图形界面查看数据库](#10-用-tableplus-图形界面查看数据库)
11. [docker compose 里的服务是什么](#11-docker-compose-里的服务是什么)
12. [常见问题排查](#常见问题排查)
13. [附录：手机真机访问 API](#附录手机真机访问-api)

---

## 快速路线：最少步骤跑通

下面 5 步做完，你就已经「从 0 到 1」跑通整套（**不需要先装 Python 虚拟环境**，除非你打算本机跑 `uvicorn`）。

1. **安装并打开 [Docker Desktop](https://www.docker.com/products/docker-desktop/)**，等菜单栏图标就绪（鲸鱼不再显示 “starting”）。
2. **打开终端**（Mac：`终端.app`；Windows：`PowerShell` 或 `cmd`）。
3. **进入项目根目录**（里面有 `docker-compose.yml` 的那一层）：
   ```bash
   cd /你的路径/PYTest
   ```
4. **执行**（第一次会下载镜像，可能较慢）：
   ```bash
   docker compose up --build
   ```
5. **浏览器打开** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)，在页面里找到 **`POST /items/`** → **Try it out** → 填 JSON → **Execute**。若返回 **201** 且 body 里有 `id`，说明**写入数据库成功**。

做到这里可以先庆祝一下。终端里会一直刷日志，**要停掉服务**：在运行 `docker compose` 的那个窗口按 **`Ctrl + C`**。

---

## 零基础概念速览

### 后端、API、JSON 是什么？

- **后端（服务器）**：跑在你电脑或云上的程序，负责**存数据、校验规则、业务逻辑**。你的 **iOS App** 或浏览器是**客户端**，通过网络问后端要数据或提交数据。
- **API**：约定好的「网址 + 动作」。例如「用 **POST** 访问 **`/items/`**，带上 **JSON**」，表示「新建一条记录」。
- **JSON**：一种文本格式，像字典：`{"title":"书名","description":"备注"}`。和 Swift 里的 `Codable` 传的数据形状类似。

### Docker 是干什么的？为什么要用？

- **问题**：每个人电脑上的 Python 版本、装的库不一样，容易出现「我这边能跑你那边报错」。
- **Docker**：把「运行环境 + 依赖 + 启动方式」打成一个**镜像（image）**，跑起来叫**容器（container）**。别人用同一套文件，行为更接近一致。
- **docker compose**：一个配置文件里写好几个服务（例如 **数据库一个容器、API 一个容器**），一条命令一起启动。

### 镜像 vs 容器（别混）

| 概念 | 比喻 | 说明 |
|------|------|------|
| **镜像** | 安装包 / 模板 | 只读，可重复用来创建多个容器。 |
| **容器** | 正在运行的实例 | 有进程、有网络；删了容器，镜像还在。 |

### 端口是什么？为什么老提 8000 和 5432？

- 一台机器上有很多程序，**端口**像「门牌号」，用来区分不同服务。
- **8000**：本项目里 **HTTP API（网页能访问的那个）** 使用的端口（在 `docker-compose.yml` 和 Dockerfile 里约定好的，可以改，但要一起改）。
- **5432**：**PostgreSQL 数据库**的默认端口。TablePlus 连本机数据库时，要填这个端口（除非你在 compose 里改成了别的映射）。

### 请求是怎样到达数据库的？

用一句话串起来：

**浏览器 / App** →（HTTP）→ **FastAPI（Uvicorn，端口 8000）** →（SQLAlchemy）→ **PostgreSQL（端口 5432）**

Docker 里 **API 容器**和 **数据库容器**在同一网络里，API 用主机名 **`db`** 找到数据库（不是 `localhost`，那是「自己这个容器」）。

---

## 开始前：你要安装什么

### 必装：Docker Desktop

- 下载：[Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **验证**：终端执行
  ```bash
  docker --version
  docker compose version
  ```
  有版本号输出即可。
- **常见坑**：没打开 Docker Desktop 就运行 `docker compose`，会报 **cannot connect to Docker daemon** —— 先打开软件，等完全启动再试。

### 建议安装：Python 3（用于本机调试、课堂作业扩展）

- 下载：[python.org](https://www.python.org/downloads/)（安装时勾选 **Add Python to PATH**（Windows））。
- **验证**：
  ```bash
  python3 --version
  ```
  Windows 上若无效可试：`python --version`。

> **说明**：只用 Docker 跑全套时，**可以不建 venv**；但只要你打算在终端里运行 `pip` / `uvicorn`，建议用下一节的虚拟环境，避免把包装进系统 Python。

---

## 4. 构建 Python 环境（可选，但建议做）

### 4.1 为什么要虚拟环境（`.venv`）？

把本项目用到的包装在**项目文件夹里的独立环境**中，不污染系统 Python，也方便和 `requirements.txt` 对齐。

### 4.2 操作步骤

在**项目根目录**（与 `requirements.txt` 同级）执行：

```bash
cd /你的路径/PYTest
python3 -m venv .venv
```

**激活**（每开一个新终端都要再做一次）：

- **macOS / Linux**：
  ```bash
  source .venv/bin/activate
  ```
- **Windows（PowerShell）**：
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

提示符前出现 `(.venv)` 表示已激活。然后：

```bash
pip install -r requirements.txt
```

### 4.3 `requirements.txt` 里是什么？

| 包 | 通俗作用 |
|----|----------|
| `fastapi` | 写 Web API 的框架 |
| `uvicorn[standard]` | 真正监听端口、处理请求的 Web 服务器 |
| `sqlalchemy` | **ORM**：用 Python 类表示表，少写裸 SQL |
| `psycopg2-binary` | 让 Python 能连 **PostgreSQL** |

Docker 构建 API 镜像时也会读**同一份** `requirements.txt` 安装依赖。

---

## 5. 理解项目里的 Docker 相关文件

这些文件都是**纯文本**，用 VS Code / Cursor 新建、保存即可；**Docker Desktop 不会**根据你的业务自动生成它们。

### 5.1 目录结构（和本教程相关的部分）

```
PYTest/
├── app/
│   ├── main.py              # 应用入口：建表、挂载路由、/health 等
│   ├── database.py          # 数据库地址、连接池、每次请求用的 Session
│   ├── models.py            # 表结构（ORM）
│   ├── schemas.py           # 接口上的 JSON 形状（校验用）
│   ├── crud.py              # 增删改查函数（不管 HTTP 状态码）
│   └── routers/items.py     # /items 的 URL 与 GET/POST 等
├── requirements.txt
├── Dockerfile               # 「如何制作 API 镜像」
├── docker-compose.yml       # 「起哪些容器、端口、环境变量」
├── .dockerignore            # 构建时不要拷贝哪些文件（如 .venv）
└── TUTORIAL.md              # 本教程
```

### 5.2 `Dockerfile`（只做一件事：描述 API 镜像）

- 从官方 **Python 3.12** 精简镜像开始，安装依赖，复制 `app/`。
- 启动命令：`uvicorn app.main:app --host 0.0.0.0 --port 8000`  
  - **`0.0.0.0`**：在容器**内部**监听所有网卡；若只写 `127.0.0.1`，宿主机浏览器会连不上。

### 5.3 `docker-compose.yml`（编排：数据库 + API）

- **`db`**：使用官方 **PostgreSQL** 镜像；数据放在卷 **`pgdata`** 里，容器删了数据一般还在。
- **`api`**：用当前目录的 `Dockerfile` **构建**并运行；把本机 **8000** 映射到容器 **8000**。
- **`DATABASE_URL`**：告诉程序数据库在哪。在 **api 容器里**主机名是 **`db`**（服务名），不是 `localhost`。
- **`depends_on` + `healthcheck`**：等数据库**就绪**再起 API，减少「一启动就连库失败」。

### 5.4 `.dockerignore`

避免把 `.venv`、`.git` 等大文件夹发给 Docker 构建进程，**加快构建、减小镜像无关内容**。

---

## 6. 用一条命令起 API + 数据库

在项目根目录：

```bash
docker compose up --build
```

- **`--build`**：如果 Python 代码或 `Dockerfile` 变了，重新构建 **api** 镜像。
- 第一次会 **pull** Postgres 镜像、安装 pip 包，**耐心等待**。
- 日志里若出现 **Uvicorn running on http://0.0.0.0:8000** 且无连续报错，通常表示 API 已监听。

**后台运行**（终端不占用，适合长期挂着）：

```bash
docker compose up --build -d
```

查看是否在跑：

```bash
docker compose ps
```

**停止并删除容器**（数据卷默认保留，数据库文件还在）：

```bash
docker compose down
```

### 另一种开发方式：只把数据库放在 Docker 里

```bash
docker compose up -d db
source .venv/bin/activate   # 若已建 venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

此时 API 跑在本机，数据库仍用映射到 **localhost:5432** 的容器；`app/database.py` 里默认连接串已是 `localhost`。

---

## 7. 起服务之后：Python 代码各自干什么

| 文件 | 一句话 |
|------|--------|
| `main.py` | 创建 `FastAPI` 应用；启动时 **建表**；把 **`/items`** 路由挂上去。 |
| `database.py` | 读环境变量 **`DATABASE_URL`**；创建 **引擎** 和 **会话工厂**；`get_db` 给每个 HTTP 请求一个数据库会话并在结束时关闭。 |
| `routers/items.py` | 把 URL（如 `POST /items/`）接到具体函数上；查不到时返回 **404**。 |
| `crud.py` | 真正执行 **增删改查**（`add` / `commit` / `query` 等），**不知道** HTTP。 |
| `models.py` | **表**长什么样（列名、类型）。 |
| `schemas.py` | **接口**上 JSON 长什么样（创建时要不要 `id`、返回时要不要 `created_at`）。 |

**为什么要分 `models` 和 `schemas`？**  
表结构会随时间变，对外接口往往要**隐藏内部字段**或**改名**；分开写更清晰，也和移动端 **DTO / Codable** 分层类似。

---

## 8. 数据库与增删改查（CRUD）

### 8.1 「数据库已经建好了吗？」

- **库与用户**：第一次启动 **`db` 容器**时，由环境变量自动创建（用户 `app`，库 `appdb`）。
- **表 `items`**：第一次启动 **API** 时，代码里 **`create_all`** 会根据 `models.py` 创建（若表已存在则不会清空数据）。

### 8.2 CRUD 和 HTTP 方法对应关系（背这个很有用）

| 想做的事 | HTTP 方法 | 本项目的路径（前缀都是 `/items`） |
|----------|-----------|-------------------------------------|
| **C**reate 创建 | POST | `POST /items/` |
| **R**ead 列表 | GET | `GET /items/` |
| **R**ead 单条 | GET | `GET /items/{id}` |
| **U**pdate 更新 | PATCH | `PATCH /items/{id}` |
| **D**elete 删除 | DELETE | `DELETE /items/{id}` |

### 8.3 创建时 JSON 长什么样？

```json
{
  "title": "必填字符串",
  "description": "可选，没有就写 null 或删掉这个字段"
}
```

---

## 9. 如何验证是否成功

按下面顺序检查；**任一步失败**就到 [常见问题排查](#常见问题排查)。

| 步骤 | 做什么 | 怎样算成功 |
|------|--------|------------|
| 1 | `docker compose ps` | `db`、`api` 状态为 **running**（若你起了全套） |
| 2 | 浏览器打开 [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) | 看到 JSON，里面有 `"status":"ok"` |
| 3 | 打开 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | 能看到一堆接口列表，不是「无法连接」 |
| 4 | 在 `/docs` 里调 **`POST /items/`** | **Response code 201**，body 里有 **`id`**、**`created_at`** |
| 5 | 再调 **`GET /items/`** | 能看到刚创建的那条 |

### 用 curl 再试一次（可选）

```bash
curl -s http://127.0.0.1:8000/health
```

```bash
curl -s -X POST "http://127.0.0.1:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"title":"curl 测试","description":null}'
```

### `/docs` 里的三个词是什么意思？

- **127.0.0.1**：只访问**你自己这台电脑**上的服务。
- **8000**：API 占用的端口。
- **`/docs`**：FastAPI **自动生成**的交互式文档（Swagger），方便测试，**不是**你手写的网页。

### 命令行直接查表（可选）

```bash
docker compose exec db psql -U app -d appdb -c "SELECT id, title FROM items;"
```

---

## 10. 用 TablePlus 图形界面查看数据库

### 10.1 安装

官网：[TablePlus](https://tableplus.com)（有免费版；Mac / Windows 都有）。

### 10.2 连接前

确保数据库容器在跑，例如：

```bash
docker compose up -d db
```

（若 API 也在 Docker 里，通常 `docker compose up -d` 即可。）

### 10.3 新建连接（PostgreSQL）

填写（与当前 `docker-compose.yml` 一致）：

| 字段 | 值 |
|------|-----|
| Host | `127.0.0.1` |
| Port | `5432` |
| User | `app` |
| Password | `appsecret` |
| Database | `appdb` |

先点 **Test**，再 **Connect**。

### 10.4 找到表和数据

左侧进入 **`public` → `Tables` → `items`**，切到 **Data**（数据）视图。你在 `/docs` 里 **POST** 创建的行应出现在这里。

> **注意**：若改了 compose 里的密码或端口，这里也要一起改。

---

## 11. docker compose 里的服务是什么？

本项目 **`services:`** 下只有两个名字：

| 服务名 | 是什么 |
|--------|--------|
| **db** | PostgreSQL 数据库 |
| **api** | FastAPI（Uvicorn） |

**常用命令**：

```bash
docker compose up -d           # 后台启动 compose 文件里所有服务
docker compose up -d db        # 只启动数据库
docker compose stop api        # 只停 API，数据库可继续跑
docker compose logs -f api     # 只看 API 日志（排错用）
```

**为什么有时说「只起 db」？**  
例如你只想用 TablePlus 看库，或本机跑 `uvicorn` 调试，不需要 API 容器。

---

## 常见问题排查

### Docker 相关

| 现象 | 可能原因 | 试试 |
|------|----------|------|
| `Cannot connect to the Docker daemon` | Docker Desktop 没开 | 打开 Docker Desktop，等就绪后再执行命令 |
| `port is already allocated` | 8000 或 5432 被占用 | 关掉占用端口的程序，或改 `docker-compose.yml` 里 **左侧**端口（如 `"8001:8000"`），浏览器改用 8001 |
| 构建很慢 | 第一次要下镜像 | 正常；可换网络或使用镜像加速（视学校/地区而定） |

### API / 数据库相关

| 现象 | 可能原因 | 试试 |
|------|----------|------|
| 浏览器打不开 `/docs` | API 没起来或端口不对 | `docker compose ps`；看终端是否还在跑 `up`；URL 端口是否和 compose 一致 |
| `POST /items/` 报 500 | 数据库连不上 | 确认 `db` 在跑；看 `docker compose logs api` 里错误信息 |
| TablePlus 连不上 | db 没起或端口错 | `docker compose ps`；端口是否仍为 5432 |

### Python / venv 相关

| 现象 | 可能原因 | 试试 |
|------|----------|------|
| `command not found: uvicorn` | 没激活 venv 或没装依赖 | `source .venv/bin/activate` 后 `pip install -r requirements.txt` |
| Windows 无法 `activate` | 执行策略限制 | 以管理员身份开 PowerShell：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## 附录：手机真机访问 API

- **iOS 模拟器**：仍可用 `http://127.0.0.1:8000`。
- **真机**：手机和电脑同一 Wi‑Fi，把 `127.0.0.1` 换成电脑的**局域网 IP**（如 `http://192.168.1.10:8000`）。  
- 仅用 **HTTP** 时，iOS 需在 **Info.plist** 里配置 **App Transport Security** 例外，否则系统会拦截。

---

## 学完后你可以自豪地说…

- 我用 **Docker Compose** 同时跑起了 **API 容器**和 **Postgres 容器**，并理解了 **端口映射**。
- 我知道 **FastAPI** 提供 HTTP 接口，**SQLAlchemy** 访问数据库，**`/docs`** 是自动文档。
- 我能用 **TablePlus** 连上本机 **5432**，看到 **`items`** 表里的数据。

若要继续深入，下一步通常是：**用户登录（JWT）**、**用 Alembic 管理表结构变更**、**把 compose 部署到云服务器**。需要时可在此基础上扩展新章节。

---

*文档与仓库内 `docker-compose.yml`、账号密码一致；若你修改了 compose，请同步更新本文表格中的连接信息。*
