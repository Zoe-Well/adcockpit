# Tasks: AdCockpit v2.0 — Full-Stack Rewrite

**Input**: Design documents from `specs/001-adcockpit-system-spec/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, constitution.md ✅, clarifications ✅

**Tests**: Included — pytest backend + Vitest frontend

---

## Phase 1: Project Scaffold

**Purpose**: Initialize both frontend and backend projects with correct toolchains.

- [ ] **T001** 创建 `backend/` 目录结构：`backend/app/{api,agents,tools,memory,tasks,core}`，含各子目录 `__init__.py`
- [ ] **T002** 创建 `backend/requirements.txt`：fastapi, uvicorn, langgraph>=1.0, langchain>=1.2, langchain-openai, celery, redis, chromadb, python-dotenv, httpx, sse-starlette
- [ ] **T003** [P] 初始化 React 项目 `frontend/`：使用 `npm create vite@latest frontend -- --template react-ts`，安装 tailwindcss, @tailwindcss/vite, shadcn/ui
- [ ] **T004** [P] 配置 `frontend/tailwind.config.ts` 和 shadcn/ui 组件库初始化
- [ ] **T005** [P] 创建 `backend/app/core/config.py`：读取 .env（DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, REDIS_URL, CHROMA_HOST, FEISHU_*），Pydantic Settings 类

---

## Phase 2: Backend Foundation (Blocking)

**Purpose**: Core backend infrastructure — FastAPI app, LangGraph agents, DeepSeek LLM, 24 tools.

**⚠️ BLOCKS all user story phases.**

- [ ] **T006** 迁移 `agents/state.py` → `backend/app/agents/state.py`：保持 AgentState TypedDict 不变
- [ ] **T007** [P] 迁移 8 个 Agent 节点到 `backend/app/agents/`：supervisor, data_agent, analysis_agent, strategy_agent, content_agent, ecommerce_agent, execute_agent, report_agent
- [ ] **T008** [P] 迁移 `tools/mock_functions.py` + `tools/mock_data.py` → `backend/app/tools/`：24 个 Mock 函数保持不变
- [ ] **T009** [P] 迁移 `tools/feishu_client.py` → `backend/app/tools/feishu_client.py`
- [ ] **T010** 创建 `backend/app/core/llm.py`：DeepSeek 模型初始化，使用 `ChatOpenAI`（base_url=https://api.deepseek.com/v1, model=deepseek-chat），支持 Function Calling
- [ ] **T011** 构建 `backend/app/agents/graph.py`：LangGraph StateGraph，8 节点 + 条件边，MemorySaver checkpoint，调用 `app/core/llm.py` 的 DeepSeek 实例
- [ ] **T012** 创建 `backend/app/api/main.py`：FastAPI app，CORS 允许 localhost:3000，include 各 router
- [ ] **T013** [P] 创建 `backend/app/api/campaigns.py`：GET /api/campaigns, GET /api/campaigns/all, POST /api/campaigns/optimize, POST /api/campaigns/create
- [ ] **T014** [P] 创建 `backend/app/api/content.py`：POST /api/content/generate, POST /api/content/publish
- [ ] **T015** [P] 创建 `backend/app/api/intent.py`：POST /api/intent/classify（复用 agents/supervisor 意图分类逻辑）

**Checkpoint**: `uvicorn backend.app.api.main:app --port 8000` 应可启动，API 端点可调用。

---

## Phase 3: Celery + Redis + WebSocket (Async Infrastructure)

**Purpose**: Async agent execution, session storage, real-time streaming.

- [ ] **T016** 创建 `backend/app/core/celery_app.py`：Celery 实例，Redis broker，任务序列化配置
- [ ] **T017** 创建 `backend/app/tasks/agent_tasks.py`：Celery 任务 `run_agent_task(session_id, user_input, params)`，内部调用 `graph.invoke()`，每节点完成后通过 WebSocket 推送状态。支持软取消（检查 `cancel_flag:{session_id}` Redis key）
- [ ] **T018** 创建 `backend/app/memory/session_store.py`：Redis 会话存储，`save_session(sid, data, ttl=3600)`, `get_session(sid)`, `delete_session(sid)`
- [ ] **T019** 创建 `backend/app/api/ws.py`：FastAPI WebSocket 端点 `/ws/{session_id}`，维护连接池 `{sid: [websocket]}`, 提供 `push_event(sid, event)` 方法供 Celery 任务调用
- [ ] **T020** 更新 `backend/app/api/campaigns.py` optimize 端点：改为 `POST /api/campaigns/optimize` → 创建 Celery 任务 → 立即返回 `{task_id, status: "processing"}`；前端通过 WebSocket 接收步骤推送
- [ ] **T021** [P] 创建 `backend/app/api/tasks.py`：GET /api/tasks/{task_id}/status 查询 Celery 任务状态，GET /api/tasks/{task_id}/result 获取结果

**Checkpoint**: `redis-server` + `celery -A backend.app.core.celery_app worker` 启动，POST optimize 返回 task_id，WebSocket 推送步骤。

---

## Phase 4: Chroma RAG (Long-Term Memory)

**Purpose**: Store historical optimization records for retrieval-augmented generation.

- [ ] **T022** 创建 `backend/app/memory/chroma_store.py`：Chroma 客户端初始化（embedded 模式），collection `optimization_history`，embedding 使用 DeepSeek
- [ ] **T023** 实现 `add_optimization_record(plan_id, params, changes, result)`：将优化记录向量化存入 Chroma，metadata 含 plan_id, timestamp, roi_before, roi_after
- [ ] **T024** 实现 `search_similar_cases(query, k=3)`：检索与当前场景最相似的历史优化案例，返回 top-k
- [ ] **T025** 更新 `backend/app/agents/strategy_agent.py`：策略生成前调用 `search_similar_cases` 检索历史案例，注入 LLM prompt 作为 few-shot 参考
- [ ] **T026** 更新 `backend/app/agents/report_agent.py`：报告生成时引用历史案例对比（"上次类似案例 ROI 提升 12%，本次预计提升 10%"）

**Checkpoint**: 执行一次优化后 Chroma 中有记录，再次优化时 Agent 能引用历史案例。

---

## Phase 5: React Frontend — US1 投放优化 (P1) 🎯 MVP

**Goal**: 完整的投放优化 U I 链路——对话输入 → 意图识别 → 参数卡片 → WebSocket 流式追踪 → Dashboard 更新。

**Independent Test**: 输入"检查最近7天抖音ROI低于2的计划"，验证 Trace Board 逐步点亮，Dashboard 显示正确数据。

- [ ] **T027** [P] [US1] 创建 `frontend/src/types/index.ts`：TypeScript 类型定义（Campaign, OptimParams, TraceEvent, ChatMessage, DashboardData, WebSocketEvent）
- [ ] **T028** [P] [US1] 创建 `frontend/src/lib/api.ts`：API 客户端（fetch /api/campaigns, /api/intent/classify, /api/content/generate），统一错误处理
- [ ] **T029** [P] [US1] 创建 `frontend/src/hooks/useWebSocket.ts`：WebSocket hook（连接 /ws/{sid}，自动重连，消息分发）
- [ ] **T030** [US1] 创建 `frontend/src/App.tsx`：三栏布局（sidebar 200px + Chat 30% + Trace 28% + Dashboard 42%），使用 Tailwind grid
- [ ] **T031** [US1] 创建 `frontend/src/components/layout/Sidebar.tsx`：6 个导航按钮（投放优化/新建计划/内容生产/直播监控/数据分析/故障诊断），底部用户信息
- [ ] **T032** [P] [US1] 创建 `frontend/src/components/chat/ChatPanel.tsx`：消息列表（user/agent 气泡），输入框 + 发送按钮，滚动到底
- [ ] **T033** [P] [US1] 创建 `frontend/src/components/chat/ParamCard.tsx`：优化参数表单（平台多选、天数 slider、ROI 阈值、出价/预算调整 %），"开始优化"+"取消"按钮
- [ ] **T034** [P] [US1] 创建 `frontend/src/components/trace/FlowTracker.tsx`：水平流程图（7 节点圆点 + 连线），done（绿）/active（蓝）/wait（黄）/pending（灰）状态
- [ ] **T035** [P] [US1] 创建 `frontend/src/components/trace/StepCard.tsx`：步骤卡片组件，状态图标 + 标题 + 描述文字 + 结果摘要
- [ ] **T036** [P] [US1] 创建 `frontend/src/components/trace/TraceBoard.tsx`：组合 FlowTracker + StepCard 列表，从 WebSocket 事件驱动状态更新
- [ ] **T037** [P] [US1] 创建 `frontend/src/components/dashboard/MetricCard.tsx`：指标卡片（label, value, sub, trend, alert）
- [ ] **T038** [P] [US1] 创建 `frontend/src/components/dashboard/ChartWidget.tsx`：ROI 柱状图（低阈值红色高亮 + 虚线阈值线）
- [ ] **T039** [P] [US1] 创建 `frontend/src/components/dashboard/CampaignTable.tsx`：分页表格（5条/页，排序，ROI 红色高亮）
- [ ] **T040** [US1] 创建 `frontend/src/components/dashboard/Dashboard.tsx`：组合 MetricCard + ChartWidget + CampaignTable + AlertList，根据 activeTab 切换视图
- [ ] **T041** [US1] 集成 ChatPanel + TraceBoard + Dashboard 到 App.tsx：发送消息 → API 意图分类 → 渲染 ParamCard 或回复文本 → 提交优化 → WebSocket 推送 → TraceBoard 动画 → Dashboard 刷新

**Checkpoint**: `npm run dev` → 打开 localhost:3000，投放优化 UI 完整可用。

---

## Phase 6: React Frontend — US2-US5 其他场景

**Goal**: 完成新建计划、内容生产、直播监控、数据分析、故障诊断的 UI。

### US2: 新建计划 (P2)

- [ ] **T042** [P] [US2] 创建 `frontend/src/components/chat/CreateForm.tsx`：新建计划表单（平台、名称、预算、出价、定向）
- [ ] **T043** [US2] 对接 POST /api/campaigns/create，成功后显示 Trace Board 创建流程

### US3: 内容生产 (P2)

- [ ] **T044** [P] [US3] 更新 ParamCard 支持内容生产参数（平台、日期、TopN、模板、自动发布开关）
- [ ] **T045** [US3] 对接 POST /api/content/generate → 展示脚本预览 → 确认 → POST /api/content/publish

### US4: 数据分析 (P2)

- [ ] **T046** [P] [US4] 创建 `frontend/src/components/dashboard/DataDashboard.tsx`：客户 ROI 排名柱状图 + 预算建议表 + PPT 提纲

### US5: 故障诊断 (P3)

- [ ] **T047** [P] [US5] 创建 `frontend/src/components/dashboard/DiagnosisDashboard.tsx`：根因卡片 + 恢复日志时间线

---

## Phase 7: Docker + Testing

**Purpose**: One-command deployment and full test coverage.

- [ ] **T048** [P] 创建 `docker-compose.yml`：services: frontend (nginx), backend (uvicorn), celery-worker, redis, chroma。端口映射 3000:80, 8000:8000
- [ ] **T049** [P] 创建 `backend/Dockerfile`：python:3.11-slim，安装依赖，CMD uvicorn
- [ ] **T050** [P] 创建 `frontend/Dockerfile`：node:20-alpine build → nginx:alpine serve
- [ ] **T051** [P] 创建 `backend/tests/test_api.py`：pytest + httpx AsyncClient，测试 /api/campaigns, /api/intent, /api/content 端点
- [ ] **T052** [P] 创建 `backend/tests/test_agents.py`：测试 supervisor 场景路由、data_agent 数据拉取、strategy_agent 策略生成
- [ ] **T053** [P] 创建 `frontend/src/__tests__/`：Vitest + React Testing Library，测试 ParamCard 渲染、TraceBoard 状态更新、Dashboard 数据展示

---

## Dependencies & Execution Order

```
Phase 1 (Scaffold) ──► Phase 2 (Backend) ──► Phase 3 (Celery+Redis+WS) ──► Phase 4 (Chroma RAG)
                          │                                                      │
                          └──────────────────┬───────────────────────────────────┘
                                             ▼
                                    Phase 5 (Frontend US1 MVP)
                                             │
                                             ▼
                              Phase 6 (Frontend US2-US5) ──► Phase 7 (Docker+Tests)
```

- Phase 2 BLOCKS all frontend phases
- Phase 3 required for WebSocket streaming in Phase 5
- Phase 4 optional for MVP (RAG can be added later)
- Phase 5 (US1) = MVP

## MVP Scope

Complete **Phase 1 + 2 + 3 + 5** (T001-T041 = 41 tasks) for a working v2.0 MVP:
- React three-column cockpit
- Backend FastAPI + LangGraph + DeepSeek
- Celery async + WebSocket streaming
- Full US1 投放优化 flow

## Task Stats

| Phase | Tasks | Story |
|-------|-------|-------|
| Scaffold | T001-T005 | — |
| Backend | T006-T015 | — |
| Celery+Redis+WS | T016-T021 | — |
| Chroma RAG | T022-T026 | — |
| Frontend US1 | T027-T041 | US1 (P1) |
| Frontend US2 | T042-T043 | US2 (P2) |
| Frontend US3 | T044-T045 | US3 (P2) |
| Frontend US4 | T046 | US4 (P2) |
| Frontend US5 | T047 | US5 (P3) |
| Docker+Tests | T048-T053 | — |
| **Total** | **53 tasks** | 5 stories |
