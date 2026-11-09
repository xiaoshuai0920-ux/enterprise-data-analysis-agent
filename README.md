# Enterprise Data Analysis Agent

一个用于演示企业 BI 自然语言分析流程的全栈项目。用户输入业务问题后，后端将问题转换为受控查询计划，按演示用户的数据范围查询指标，并返回图表和文字结论。

## 功能流程

```text
自然语言问题
  → 问题解析与查询计划
  → 语义层选择指标和维度
  → 结合用户区域范围生成 SQL
  → SQL 安全校验与只读查询
  → 生成可视化描述和分析结论
  → 前端展示图表、计划、SQL 和 Trace ID
```

当前演示模式使用确定性规则解析问题，并生成模拟分析结论；不需要 DeepSeek API 密钥。演示数据由启动脚本生成，共 144 条销售指标记录（2026 年 1 月至 9 月、4 个区域、4 个产品）。

## 技术栈

- 前端：React 19、TypeScript、Vite、ECharts
- 后端：Python 3.13、FastAPI、Pydantic、LangGraph、SQLAlchemy Async
- 数据与缓存：PostgreSQL 16、Redis 7（Docker Compose）
- 查询防护：SQLGlot，只允许访问 `sales_metrics` 的只读 `SELECT` 查询

## 启动

### Docker Compose（推荐）

需要安装并启动 Docker Desktop，然后在项目根目录运行：

```bash
docker compose up --build
```

首次启动会构建前后端镜像、启动 PostgreSQL 和 Redis，并由后端容器初始化演示数据。访问：

- 前端：http://localhost:8080
- 后端健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/docs

停止服务：

```bash
docker compose down
```

PostgreSQL 数据保存在 Docker 命名卷 `postgres_data` 中。若要同时清除该数据库卷和演示数据，可运行 `docker compose down -v`。

### 本地开发

后端需要 Python 3.13 和 `backend/requirements.txt` 中的依赖；前端需要 Node.js 22 或兼容版本。启动前后端前，需先提供 PostgreSQL 和 Redis，或在后端环境变量中改用 SQLite 及可用的 Redis 实例。示例环境变量见 `backend/.env.example`。

```bash
# 终端 1：后端（从 backend 目录执行）
python -m pip install -r requirements.txt
python -m app.scripts.seed_demo
uvicorn app.main:app --reload --port 8000

# 终端 2：前端（从 frontend 目录执行）
npm install
npm run dev
```

开发前端地址为 http://localhost:5173；Vite 会将 `/api` 和 `/health` 请求代理到 `localhost:8000`。如需连接真实模型，设置 `MOCK_MODE=false` 和 `DEEPSEEK_API_KEY`。不要将密钥提交到 Git。

## 代码结构

```text
backend/
  app/main.py                 FastAPI 应用和路由入口
  app/api/routes/             分析接口、指标元数据接口
  app/agent/                  LangGraph 状态与分析流程
  app/core/                   配置、演示身份权限、Trace
  app/models/schemas.py       请求、查询计划、图表和响应模型
  app/llm/                    DeepSeek 总结与模拟总结
  app/services/               计划解析、语义层、SQL 构造与校验、数据库、缓存、可视化
  app/scripts/seed_demo.py    演示数据初始化
  tests/                      SQL 防护和计划解析测试
frontend/
  src/App.tsx                 页面状态和交互
  src/api/                    后端 SSE 流式 API 客户端
  src/components/             图表、表格和可视化面板
  src/types/                  前后端响应的 TypeScript 类型
docker-compose.yml            PostgreSQL、Redis、后端、前端服务编排
```

## 分析接口

- `POST /api/v1/analysis`：返回完整分析结果。
- `POST /api/v1/analysis/stream`：使用 Server-Sent Events 逐步返回状态、计划、SQL、可视化和结论。
- `GET /api/v1/meta/metrics`：返回当前支持的指标和维度。
- `GET /health`：返回服务状态和当前模型模式。

前端演示请求通过 `x-user-role` 等请求头指定身份。后端把角色映射到固定区域范围，并将范围写入 SQL 条件。该身份机制只用于本地演示，不能作为生产环境认证或授权方案。

## 当前演示边界

- 演示数据是固定随机种子生成的样例数据，不代表真实企业经营情况。
- 默认 `MOCK_MODE=true`，结论由本地规则生成，不会调用外部模型。
- 查询计划支持的指标、维度和时间范围以 `backend/app/services/` 中的实现为准；这不是通用 SQL Agent。
- 请求头身份校验仅为演示用途，生产部署前需接入可信的认证与授权机制。
