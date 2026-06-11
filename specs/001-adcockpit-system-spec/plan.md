# Implementation Plan: AdCockpit 数字营销 AI Agent 系统

**Branch**: `001-adcockpit-system-spec` | **Date**: 2026-06-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-adcockpit-system-spec/spec.md`

**Note**: This plan covers the full AdCockpit system implementation — LangGraph agent
graph, Mock tool layer, FastAPI SSE backend, and Streamlit three-column cockpit UI.

## Summary

Build AdCockpit, a three-column conversational cockpit that orchestrates 8 AI agents
(Supervisor, Data, Analysis, Strategy, Content, Ecommerce, Execute, Report) via
LangGraph to automate digital marketing tasks across 4 business domains. The UI
precisely replicates the HTML prototype's dark control-panel aesthetic using Streamlit
with custom CSS injection. All platform APIs are mocked with 24 functions that return
prototype-consistent data. Real-time step streaming via SSE connects LangGraph
execution to the frontend TraceBoard component.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, LangGraph (>=0.2), Streamlit (>=1.28), sse-starlette,
pytest + pytest-asyncio + httpx
**Storage**: In-memory + local JSON files (session state, user preferences, mock data seeds)
**Testing**: pytest with pytest-asyncio; 5 scenario integration tests + unit tests for Mock functions
**Target Platform**: Windows/macOS/Linux desktop browser (1920×1080), local single-user
**Project Type**: web-service (FastAPI backend + Streamlit frontend, single process orchestrated)
**Performance Goals**: Agent graph execution < 60s end-to-end; SSE event latency < 2s;
Dashboard view switch < 1s
**Constraints**: 95%+ code AI-generated; zero external API dependencies; single `streamlit run` launch
**Scale/Scope**: 1 concurrent user (Demo), 5 scenarios, 24 Mock functions, 8 agents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. 三栏对话驾驶舱 UI | Three-column layout (25%/40%/35%), no pure chat interface | ✅ PASS |
| II. Multi-Agent 编排 | LangGraph StateGraph, 8 agents, Human-in-the-loop | ✅ PASS |
| III. 四大业务域 | Ad Placement, Content, Ecommerce, Data Analysis | ✅ PASS |
| IV. AI-First 开发 | ≥95% AI-generated, Streamlit-first | ✅ PASS |
| V. Mock-First 数据模拟 | 24 Mock functions, 10%/5% error probabilities | ✅ PASS |

**Post-Design Re-check**: ✅ All constitutional principles satisfied. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-adcockpit-system-spec/
├── plan.md              # This file
├── research.md          # Phase 0: Technical decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Validation guide
├── contracts/           # Phase 1: API & SSE contracts
│   └── api-contracts.md
└── tasks.md             # Phase 2: /speckit-tasks output
```

### Source Code (repository root)

```text
adcockpit-prototype.html    # Reference prototype (static HTML)

agents/                     # LangGraph Agent 定义
├── __init__.py
├── state.py                # AgentState TypedDict
├── graph.py                # StateGraph 构建 + 编译
├── supervisor.py           # Supervisor Agent 节点
├── data_agent.py           # Data Agent 节点
├── analysis_agent.py       # Analysis Agent 节点
├── strategy_agent.py       # Strategy Agent 节点
├── content_agent.py        # Content Agent 节点
├── ecommerce_agent.py      # Ecommerce Agent 节点
├── execute_agent.py        # Execute Agent 节点 (含 HITL 中断)
└── report_agent.py         # Report Agent 节点

tools/                      # Mock 函数层
├── __init__.py
├── mock_data.py            # Mock 数据常量 (与原型一致)
├── mock_functions.py       # 24 Mock 函数实现
└── tool_registry.py        # 工具注册表 (LangChain Tool 封装)

api/                        # FastAPI 后端
├── __init__.py
├── main.py                 # FastAPI app + SSE endpoint
├── routes.py               # REST 端点
└── sse_manager.py          # SSE 事件管理器

ui/                         # Streamlit 前端
├── __init__.py
├── app.py                  # 主入口 (三栏布局)
├── theme.py                # 自定义 CSS 注入
├── panels/
│   ├── __init__.py
│   ├── chat_panel.py       # 左侧: ChatPanel
│   ├── trace_board.py      # 中间: TraceBoard
│   └── dashboard.py        # 右侧: InsightDashboard
└── components/
    ├── __init__.py
    ├── metric_card.py      # MetricCard 组件
    ├── step_card.py        # StepCard 组件
    ├── chart_widget.py     # ChartWidget 组件
    ├── approval_card.py    # ApprovalCard 组件
    └── report_summary.py   # ReportSummary 组件

tests/
├── __init__.py
├── conftest.py             # Fixtures
├── unit/
│   ├── test_mock_functions.py
│   └── test_agent_state.py
└── scenarios/
    ├── test_scenario_1_ad_placement.py
    ├── test_scenario_2_content.py
    ├── test_scenario_3_ecommerce.py
    ├── test_scenario_4_data_analysis.py
    └── test_scenario_5_diagnosis.py

requirements.txt
```

## Complexity Tracking

> No violations — all constitutional principles satisfied by design.

---

## Implementation Stages

### Stage 1: LangGraph Agent 图 + Mock 工具 (基础设施)

**目标**: 核心 Agent 编排逻辑完整可运行，Mock 函数可独立调用，HITL 中断可触发。

**文件清单**:
- `agents/state.py` — AgentState TypedDict + 子实体 (TaskNode, PlatformData, StrategyAction, ExecutionResult)
- `agents/graph.py` — StateGraph 构建 (`add_node` × 8 + `add_conditional_edges` + `interrupt()`)
- `agents/supervisor.py` — Supervisor: 语义解析 → task_graph + current_scene
- `agents/data_agent.py` — Data Agent: 并行调用 Mock 函数拉取平台数据
- `agents/analysis_agent.py` — Analysis Agent: 筛选/异常检测/分组排名/根因分析
- `agents/strategy_agent.py` — Strategy Agent: 生成 StrategyAction 列表 (含风险等级)
- `agents/content_agent.py` — Content Agent: 基于模板生成脚本/文案
- `agents/ecommerce_agent.py` — Ecommerce Agent: 库存/优惠券/直播监控
- `agents/execute_agent.py` — Execute Agent: 统一执行 + `interrupt()` HITL + 重试
- `agents/report_agent.py` — Report Agent: 聚合输出结构化报告
- `tools/mock_data.py` — Mock 数据常量 (与 `adcockpit-prototype.html` 完全一致)
- `tools/mock_functions.py` — 24 个 Mock 函数 (10% 业务异常, 5% 网络异常)
- `tools/tool_registry.py` — LangChain Tool 封装注册
- `tests/unit/test_mock_functions.py` — Mock 函数单元测试 + 原型数据一致性验证
- `tests/unit/test_agent_state.py` — AgentState 状态转换测试

**实现提示词示例**:

> **Prompt 1-AgentState**: "在 `agents/state.py` 中定义 TypedDict `AgentState`，包含:
> `user_input: str`, `task_graph: List[TaskNode]`, `platform_data: List[PlatformData]`,
> `analysis_result: Dict`, `strategy_actions: List[StrategyAction]`,
> `execution_results: List[ExecutionResult]`, `report: Dict`,
> `pending_approval: Optional[List[StrategyAction]]`,
> `conversation_history: List[Dict]`, `error_log: List[Dict]`,
> `session_id: str`, `current_scene: Literal['ad_placement','content','ecommerce',
> 'data_analysis','diagnosis']`。同时定义子 TypedDict TaskNode(id, type, platform?,
> params, depends_on, status), PlatformData(platform, endpoint, data, fetched_at, error),
> StrategyAction(target_id, target_type, action, params, risk_level, expected_effect,
> requires_approval), ExecutionResult(action, status, response, error, retry_count,
> executed_at)。字段完全按照 spec.md 中 State 定义。"

> **Prompt 2-MockData**: "在 `tools/mock_data.py` 中定义以下常量，**值必须与
> `adcockpit-prototype.html` 中的假数据完全一致**:
> - DOUYIN_PLANS: 5 条抖音计划 [C001: ROI=1.5, cost=15200; C002: ROI=2.3, cost=14100;
>   C003: ROI=3.1, cost=12800; C004: ROI=1.8, cost=9600; C005: ROI=2.5, cost=8800]
> - TENCENT_PLANS: 5 条腾讯计划 [T001: ROI=1.2, cost=12800; T002: ROI=2.8, cost=11000;
>   T003: ROI=3.5, cost=9500; T004: ROI=2.1, cost=8200; T005: ROI=2.6, cost=7600]
> - CREATIVES: 6 条素材 (高CTR 3条 + 低CTR 3条)
> - PRODUCTS: 2 个商品 (含库存 32 件等)
> - CLIENT_DATA: 5 个客户的跨平台聚合数据"

> **Prompt 3-Supervisor**: "在 `agents/supervisor.py` 中实现 Supervisor Agent 节点。
> 输入 AgentState，使用 LLM 解析 user_input 语义，识别场景类型:
> 'ROI/调价/计划'→ad_placement, '素材/脚本/视频'→content,
> '直播/库存/优惠券'→ecommerce, '报表/分析/预算'→data_analysis,
> '排查/诊断/故障'→diagnosis。填充 task_graph (6个子任务 T1-T6,
> 前2个并行), 设置 current_scene, 返回更新后的 state。"

> **Prompt 4-LangGraph**: "在 `agents/graph.py` 中构建 LangGraph StateGraph:
> START→supervisor→data_agent→analysis_agent→route_after_analysis→
> (strategy_agent|content_agent|ecommerce_agent)→execute_agent(with interrupt())→
> report_agent→END。使用 MemorySaver checkpointer 支持中断恢复。"

---

### Stage 2: FastAPI 后端 + SSE 实时推送

**目标**: LangGraph 状态变更通过 SSE 实时推送，REST 端点可触发执行和审批。

**文件清单**:
- `api/main.py` — FastAPI app, CORS, mount SSE
- `api/routes.py` — `POST /execute`, `POST /approve`, `POST /reject`, `GET /session`, `GET /stream`
- `api/sse_manager.py` — SSEManager (asyncio.Queue per session, emit/stream)

**实现提示词示例**:

> **Prompt 5-SSE**: "在 `api/sse_manager.py` 中实现 SSEManager。create_session 创建
> asyncio.Queue, emit(session_id, event_type, data) 推送事件, stream(session_id) 返回
> SSE async generator。事件类型: step_start, step_update, step_complete,
> approval_required, step_error, execution_complete。数据格式与 contracts/api-contracts.md 一致。"

> **Prompt 6-Routes**: "在 `api/routes.py` 中实现:
> POST /execute: 创建 LangGraph 图运行 (astream_events), 每个 on_chain_start/end 事件
> 通过 SSEManager 推送, NodeInterrupt 时推送 approval_required
> POST /approve, POST /reject: 通过 Command(resume=...) 恢复图执行
> GET /session/{sid}/state: 返回 AgentState 快照
> GET /stream/{sid}: SSE StreamingResponse"

---

### Stage 3: Streamlit 前端 — 三栏驾驶舱复刻原型

**目标**: 精确复刻 `adcockpit-prototype.html` 的外观和交互，通过 SSE 事件驱动。

**文件清单**:
- `ui/theme.py` — CSS 注入 (深色主题变量、动画、Scrollbar)
- `ui/app.py` — 三栏主布局 + SSE 后台监听 + 自动刷新
- `ui/panels/chat_panel.py` — ChatPanel (消息列表 + 场景标签 + 确认卡片 + 输入框)
- `ui/panels/trace_board.py` — TraceBoard (DAG 栏 + StepCard 列表)
- `ui/panels/dashboard.py` — InsightDashboard (场景路由 + MetricCard 网格 + 图表 + 告警 + 报告)
- `ui/components/metric_card.py` — 可复用 MetricCard (label/value/sub/高亮)
- `ui/components/step_card.py` — 可复用 StepCard (状态图标 + 标题 + 描述 + 工具调用展开)
- `ui/components/chart_widget.py` — 柱状图 (ROI 对比 + 2.0 阈值线)
- `ui/components/approval_card.py` — 确认卡片 (操作列表 + 确认/取消按钮)
- `ui/components/report_summary.py` — 报告预览 (指标行 + 一键复制)

**实现提示词示例**:

> **Prompt 7-Theme**: "在 `ui/theme.py` 中 inject_custom_css()，注入与
> adcockpit-prototype.html 完全一致的 CSS 变量: --bg-primary=#0f1117,
> --bg-secondary=#1a1d27, --bg-tertiary=#242836, --border=#2a2e3a,
> --accent=#4c6ef5, --success=#51cf66, --warning=#fcc419, --danger=#ff6b6b,
> --info=#22b8cf。隐藏 Streamlit 默认 header/footer。@keyframes fadeIn/slideIn/spin。"

> **Prompt 8-App**: "在 `ui/app.py` 中实现主页面。st.columns([0.25,0.40,0.35]) 三栏布局。
> 顶部栏: Logo '⚡ AdCockpit' + 场景标签 + 状态灯 + Session ID。
> 初始化 session_state: trace_events=[], chat_messages=[预置欢迎语],
> approval_pending=None, current_scene='ad_placement', dashboard_data={}, session_id。
> 后台线程: httpx 连接 /stream/{sid} SSE 端点, 将事件 append 到 trace_events。
> 定时 st.rerun() 检测新事件。左/中/右各栏调用对应 panel 渲染函数。"

> **Prompt 9-ChatPanel**: "在 `ui/panels/chat_panel.py` 中实现左侧对话面板。
> 复刻原型: 场景快捷标签 row (5个, active 高亮), 消息列表 (user 右对齐蓝底+王头像,
> agent 左对齐暗底+AI头像), 条件渲染 ApprovalCard (pending_approval 非空时
> 在列表底部渲染, 展示操作+风险标签+确认/取消按钮), 底部固定输入框+发送按钮。
> 样式匹配原型 .chat-msg, .bubble, .avatar, .approval-card。"

> **Prompt 10-TraceBoard**: "在 `ui/panels/trace_board.py` 中实现中间面板。
> 复刻原型: DAG 栏 (supervisor蓝→data青⇉data青→analysis黄→strategy紫→execute绿→report红),
> 垂直步骤卡片列表 (StepCard), 每张卡片含状态图标 (✅/🔄spin/⏸️/❌/⏳)、
> 标题行(Agent+操作+耗时)、描述、可展开工具调用详情(折叠JSON)、失败时重试按钮。
> 卡片状态样式: done=绿色左边框, running=蓝色左边框+spin, waiting=黄色左边框,
> failed=红色左边框+retry, pending=灰色半透明。"

> **Prompt 11-Dashboard**: "在 `ui/panels/dashboard.py` 中实现右侧仪表盘。
> 复刻原型: 6个MetricCard (ROI红框1.87/消耗¥37600/CPA¥38.5/活跃10/CTR3.8%/CVR4.2%,
> 含趋势箭头+颜色), ROI柱状图(10条计划, <2.0红色渐变, 虚线阈值2.0),
> 3条异常告警(T001🔴/C001🟠/C004🟡, 左边框色对应严重度),
> 报告预览(7行指标+一键复制按钮)。
> 根据 current_scene 切换 AdDashboard/ContentDashboard/EcommerceDashboard/DataDashboard。"

---

### Stage 4: 集成测试 (pytest)

**目标**: 5 个场景端到端测试全部通过，Mock 数据与原型一致，SSE 事件顺序验证。

**文件清单**:
- `tests/conftest.py` — mock_llm, test_client, seed_data, sse_events fixtures
- `tests/scenarios/test_scenario_1_ad_placement.py` — 投放优化全链路
- `tests/scenarios/test_scenario_2_content.py` — 内容生产全链路
- `tests/scenarios/test_scenario_3_ecommerce.py` — 电商场控全链路
- `tests/scenarios/test_scenario_4_data_analysis.py` — 数据分析全链路
- `tests/scenarios/test_scenario_5_diagnosis.py` — 故障诊断全链路

**实现提示词示例**:

> **Prompt 12-TestScenario1**: "在 tests/scenarios/test_scenario_1_ad_placement.py
> 中实现投放优化场景端到端测试:
> 1. POST /execute 发送投放优化指令
> 2. 收集 SSE 事件, 验证顺序: supervisor→data(douyin+tencent并行)→analysis→
>    strategy→approval_required→execute→report→execution_complete
> 3. 验证 approval_required 包含 4 条 action (C001降价10%/T001降价10%/T001降预算20%/C004降价10%)
> 4. 验证 Data Agent 返回的 plans 与原型一致 (C001 ROI=1.5, T001 ROI=1.2)
> 5. 验证最终 report 的 estimated_saving='15%', roi_improvement='2.1'"

---

### Stage 5: 联调与演示就绪

**目标**: Streamlit + FastAPI 联调通过，5 个场景可手动演示。

**实现提示词示例**:

> **Prompt 13-Integration**: "运行联调验证: streamlit run ui/app.py + uvicorn api.main:app。
> 逐一执行 5 个场景指令，确认 UI 交互与 adcockpit-prototype.html 一致:
> 步骤卡片实时更新、指标卡数据正确、柱状图配色一致、审批卡片交互正确。
> 修复所有样式或数据偏差。"

> **Prompt 14-Requirements**: "生成 requirements.txt: fastapi>=0.110, uvicorn>=0.27,
> langgraph>=0.2, langchain>=0.2, langchain-openai>=0.1, streamlit>=1.28,
> sse-starlette>=2.0, pytest>=8.0, pytest-asyncio>=0.23, httpx>=0.27,
> python-dotenv>=1.0"

---

## Mock Data Consistency Contract

> ⚠️ **CRITICAL**: 所有 Mock 数据必须与 `adcockpit-prototype.html` 保持一致。
> 这是 Demo 一致性的硬约束。

| 数据点 | 原型值 | 来源 |
|--------|--------|------|
| C001 ROI | 1.5 | mock_data.DOUYIN_PLANS[0] |
| T001 ROI | 1.2 | mock_data.TENCENT_PLANS[0] |
| C004 ROI | 1.8 | mock_data.DOUYIN_PLANS[3] |
| 整体 ROI | 1.87 | Dashboard metric_card |
| 总消耗 | ¥37,600 | Dashboard metric_card |
| 平均 CPA | ¥38.5 | Dashboard metric_card |
| CTR | 3.8% | Dashboard metric_card |
| CVR | 4.2% | Dashboard metric_card |
| 预计节省 | 15% (¥5,640) | Report summary |
| ROI 预计提升 | 1.87→2.1 | Report summary |
| 异常计划 | C001, T001, C004 | Alert list |
| 审批动作数 | 4 (降价×3 + 降预算×1) | strategy_actions |

## Dependencies Between Stages

```
Stage 1 (Agents + Mock Tools) ──► Stage 2 (FastAPI + SSE) ──► Stage 3 (Streamlit UI)
                                                                    │
                                                                    ▼
                                                          Stage 4 (Tests)
                                                                    │
                                                                    ▼
                                                          Stage 5 (Integration)
```

Each stage is a prerequisite for the next. Within each stage, independent files
can be implemented in parallel via separate AI Coding sessions.
