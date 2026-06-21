# AdCockpit v2.0 — AI 数字营销驾驶舱

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-ff6b6b)](https://langchain-ai.github.io/langgraph/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-4B6BFB)](https://deepseek.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

基于 **LangGraph Multi-Agent 编排**的全链路 AI 数字营销系统。React 三栏对话驾驶舱形态，通过自然语言驱动 6 个 Agent 协作，覆盖投放优化、计划创建、内容生产、电商场控、数据分析、故障诊断。

> 📖 完整介绍：[docs/01-项目完整介绍](docs/01-项目完整介绍.md)  
> 🏗️ 架构详解：[docs/07-核心架构知识详解](docs/07-核心架构知识详解.md)  
> 🚀 部署指南：[docs/08-部署实战指南](docs/08-部署实战指南.md)

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 20+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/your-username/adcockpit.git
cd adcockpit
```

### 2. 启动后端

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example backend/.env
# 编辑 backend/.env，填入你的 DeepSeek API Key
# 获取地址：https://platform.deepseek.com/api_keys

# 启动后端
cd backend
uvicorn app.api.main:app --port 8000 --reload
```

后端启动后访问 http://localhost:8000/docs 可查看交互式 API 文档。

### 3. 启动前端

```bash
cd frontend
cp .env.example .env      # VITE_API_URL 默认指向 localhost:8000
npm install
npm run dev
```

浏览器打开 http://localhost:5173 即可使用。

### 4. 使用 Docker（可选）

```bash
docker-compose up -d
# 前端 → http://localhost:80
# 后端 → http://localhost:8000
```

## 项目结构

```
adcockpit/
├── frontend/               # React 18 + TypeScript + Tailwind + shadcn/ui
│   ├── src/
│   │   ├── App.tsx         # 主应用（三栏驾驶舱）
│   │   ├── components/     # UI 组件 + ErrorBoundary
│   │   └── main.tsx        # 入口
│   ├── index.html
│   ├── .env.example        # 前端环境变量模板
│   └── package.json
├── backend/                # FastAPI + LangGraph
│   ├── app/
│   │   ├── api/            # REST + WebSocket 端点
│   │   │   ├── agent.py    # Agent 编排 API（optimize/content/create）
│   │   │   ├── intent.py   # 意图分类（DeepSeek LLM + keyword fallback）
│   │   │   ├── campaigns.py # 投放计划 CRUD
│   │   │   ├── content.py  # 脚本生成 + 飞书发布
│   │   │   ├── ws.py       # WebSocket
│   │   │   └── main.py     # FastAPI 入口 + CORS
│   │   └── agents/         # LangGraph Agent 节点
│   │       ├── graph.py    # StateGraph 定义
│   │       ├── supervisor.py   # LLM 任务规划
│   │       ├── analysis_agent.py  # LLM 异常分析
│   │       ├── strategy_agent.py  # LLM 策略生成
│   │       └── content_agent.py   # 脚本生成
│   └── data/               # JSON 数据持久化
├── tools/                  # 24 Mock Functions + Feishu Client
├── docs/                   # 项目文档（8篇）
├── ui/                     # Streamlit v1（保留可用）
├── vercel.json             # Vercel 部署配置
├── docker-compose.yml
├── requirements.txt
└── .env.example            # 后端环境变量模板
```

## 部署

### 前端 → Vercel

1. 将项目推送到 GitHub
2. 在 [vercel.com](https://vercel.com) 导入仓库
3. 设置环境变量 `VITE_API_URL` = 你的后端地址
4. Vercel 自动读取 `vercel.json` 配置，完成部署

### 后端 → Railway / Render

1. 在 [railway.app](https://railway.app) 或 [render.com](https://render.com) 导入仓库
2. 设置环境变量（`.env.example` 中的变量）
3. 启动命令：`uvicorn backend.app.api.main:app --host 0.0.0.0 --port $PORT`
4. 将后端地址填入前端的 `VITE_API_URL`

详细部署指南：[docs/08-部署实战指南](docs/08-部署实战指南.md)

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TypeScript + Tailwind CSS + shadcn/ui |
| 后端 | FastAPI + Pydantic |
| Agent | LangGraph StateGraph + MemorySaver |
| LLM | DeepSeek (v4-flash/v4-pro) via OpenAI SDK |
| 工具 | 24 Mock Functions + Feishu Open API |
| 持久化 | Local JSON（Demo）/ Redis + Chroma（Prod 就绪） |
| 实时 | WebSocket（端点就绪） |

## 文档

| 文档 | 说明 |
|------|------|
| [01-项目完整介绍](docs/01-项目完整介绍.md) | 项目定位、功能、架构全景 |
| [06-项目实现状态](docs/06-项目实现状态.md) | 每个 User Story 完成度 |
| [07-核心架构知识详解](docs/07-核心架构知识详解.md) | 从零基础理解每个技术 |
| [08-部署实战指南](docs/08-部署实战指南.md) | 从本地到生产完整流程 |
| [bug.md](docs/bug.md) | Bug 记录 |

## License

MIT
