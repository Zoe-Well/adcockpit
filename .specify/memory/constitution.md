<!--
Sync Impact Report
==================
Version change: 1.0.0 → 2.0.0 (MAJOR — architecture redesign)
Modified principles:
  - IV. AI-First 开发范式 → IV. AI-First 开发范式 + 生产级架构
Added sections:
  - 前端 React 18+ + shadcn/ui + Tailwind CSS 约束
  - Celery + Redis 异步任务约束
  - Chroma + RAG 长期记忆约束
  - WebSocket 流式推送约束
Removed sections:
  - Streamlit 相关约束
  - Mock Server 约束
Templates requiring updates:
  ✅ plan-template.md — Constitution Check 动态门禁，无需修改
  ✅ spec-template.md — 通用模板，无需修改
  ✅ tasks-template.md — 通用模板，无需修改
Follow-up TODOs: None
-->

# AdCockpit 项目宪法

> 数字营销 AI Agent 系统 —— 对话驾驶舱

## Core Principles

### I. 三栏对话驾驶舱 UI

UI 层 MUST 采用三栏布局：左侧对话面板 (Chat Panel) + 中间 Agent 编排与执行追踪
(Trace Board) + 右侧数据洞察仪表盘 (Insight Dashboard)。MUST NOT 使用纯聊天界面
或单栏 Chatbot 形态。

- 左侧面板承载自然语言输入、多轮对话澄清、历史记录、人工确认/干预弹窗。
- 中间面板承载 Multi-Agent 任务分解图谱、执行步骤流、工具调用详情 (Req/Res)、
  状态标识（等待/进行中/成功/失败/需确认）、错误重试与回滚。
- 右侧面板承载场景自适应仪表盘：投放 ROI 卡片/趋势、内容脚本预览/修改、
  电商库存/优惠券看板、数据图表/PPT 提纲、最终报告区。

**理由**: 作为 B 端服务商，客户必须能看懂 AI 在干什么、为什么这么干。三栏布局提供
透明、可干预、可交付客户的交互形态，这是纯聊天界面无法满足的业务信任要求。

### II. Multi-Agent 编排架构

系统 MUST 基于 LangGraph StateGraph 实现有状态 Multi-Agent 编排，MUST 支持
Human-in-the-loop 中断与审批机制。

- Agent 体系包含：Supervisor Agent (任务规划与动态路由)、Data Agent (多平台数据
  拉取)、Analysis Agent (数据分析与诊断)、Strategy Agent (策略生成与预算分配)、
  Content Agent (文案/脚本/视频分析)、Ecommerce Agent (库存/优惠券/直播)、
  Execute Agent (统一操作执行 + 人工确认中断)、Report Agent (可视化报告/PPT 提纲)。
- 支持并行执行、条件分支、中断与恢复。
- 每个工具调用 MUST 在中间面板完整展示输入输出、耗时和状态。
- 短期记忆通过对话历史；长期记忆存储用户偏好、爆款模板、分析维度；状态持久化支持
  中断后恢复。

**理由**: 数字营销场景天然需要多个专业角色协作。LangGraph 提供生产级的图执行、
状态管理和 Human-in-the-loop 能力，是演示"全链路数字营销服务"的技术基石。

### III. 四大业务域全覆盖

系统 MUST 覆盖以下四个核心业务域，不得遗漏任一域：

1. **广告投放优化 (Ad Placement)**: 跨平台数据分析、异常检测、自动调价/调预算、
   审核状态诊断与恢复。
2. **内容生产与分发 (Content Production)**: 投后素材分析、AI 混剪/改稿、
   多平台一键发布、内容模板记忆。
3. **电商闭环运营 (E-commerce Closed Loop)**: 直播间实时监控、自动优惠券/库存调整、
   客服话术辅助、ERP 联动。
4. **数据分析与洞察 (Data Analysis)**: 自定义报表生成、归因分析、预算分配建议、
   多平台数据聚合。

每个域 MUST 有对应的专用 Agent 和 Mock 工具函数，场景之间可联动（如投后数据驱动
内容生产、直播数据触发广告策略调整）。

**理由**: 单一投放优化场景无法体现"全链路数字营销服务"的广度。四个域覆盖了 JD 中
要求的广告、内容、电商、数据能力，每个域都可作为独立演示场景。

### IV. AI-First 开发范式 + 生产级架构

项目代码 MUST 由 AI Coding 生成不低于 95%。架构 MUST 采用标准前后端分离模式。

**前端**:
- MUST 使用 React 18+ + TypeScript + Tailwind CSS + shadcn/ui 组件库。
- MUST 展示 Agent 的思考过程和工具调用状态（中间 Trace Board 面板）。
- MUST 支持流式响应（WebSocket 实时推送 Agent 思考内容）。

**后端**:
- MUST 使用 FastAPI 提供 REST API + WebSocket 端点。
- MUST 使用 LangGraph 作为 Agent 编排框架，集成 DeepSeek 模型。
- MUST 使用 Celery 处理异步 Agent 任务。
- MUST 使用 Redis 管理会话短期记忆。
- MUST 使用 Chroma 向量数据库实现 RAG 长期记忆。

**项目结构**:
```
frontend/   (React + shadcn/ui + Tailwind)
backend/    (FastAPI + LangGraph + Celery + Redis + Chroma)
```

**理由**: 生产级架构，前后端分离便于独立部署和扩展。React+shadcn/ui 提供企业级
UI 体验，Celery+Redis 保证异步任务的可靠性，Chroma+RAG 实现智能长期记忆。

### V. Mock-First 数据模拟

所有外部平台 API MUST 使用 Mock 函数实现，MUST NOT 依赖真实平台 API 调用。

- Mock 覆盖的平台包括：巨量引擎、磁力引擎（快手）、腾讯广告、小红书聚光、
  飞书、电商 ERP。
- 每个 Mock 函数 MUST 模拟真实 API 的 Request/Response Schema，包括成功响应、
  业务异常（如审核拒绝、余额不足、超时）和网络异常（如 500、超时重试）。
- Mock 函数数量 MUST 不低于 30 个，覆盖四大业务域的核心操作。
- Mock 数据 MUST 具有内部一致性（如同一计划在不同查询中返回一致数据）。

**理由**: Demo 环境无法接入真实平台 API。高质量的 Mock 是演示 Multi-Agent 编排、
异常处理、Human-in-the-loop 等核心能力的前提。模拟真实异常才能展示系统的鲁棒性。

## 技术约束 v2.0

### 1. 强制性版本约束

| 类别 | 技术选型 | 约束 |
|------|---------|------|
| **前端框架** | React 18+ + TypeScript | MUST 使用函数组件 + Hooks |
| **UI 组件库** | shadcn/ui | 基于 Radix UI 的 headless 组件 |
| **CSS 框架** | Tailwind CSS 3+ | 原子化 CSS |
| **后端框架** | FastAPI (Python 3.11) | 所有 API 用 Pydantic 模型 |
| **Agent 框架** | LangGraph + LangChain | StateGraph + `create_agent` |
| **LLM 模型** | DeepSeek (via langchain-openai) | Function Calling 驱动 |
| **异步任务** | Celery + Redis | Agent 执行在 Celery Worker 中 |
| **WebSocket** | FastAPI WebSocket | 实时推送 Agent 思考内容 |
| **短期记忆** | Redis | 会话上下文缓存 (TTL 1h) |
| **长期记忆/RAG** | Chroma | 向量检索历史优化记录 |
| **包管理** | uv / pip | 统一依赖管理 |

### 2. 架构约束

- 前后端 MUST 完全分离，通过 REST API + WebSocket 通信。
- Agent 执行 MUST 在 Celery 异步任务中进行，避免阻塞 HTTP 请求。
- WebSocket MUST 实时推送 Agent 的中间思考步骤和工具调用结果。
- RAG 检索 MUST 在 Chroma 中完成，embedding 使用 DeepSeek 模型。

### 代码规范

- 所有 Python 代码 MUST 使用 Type Hints。
- Agent 节点 MUST 有明确的输入/输出 Schema 定义。
- Mock 工具函数 MUST 有完整的 docstring 描述参数、返回值和可能的异常。
- 前端 UI MUST 分离为独立组件，每个面板对应一个 `ui/panels/` 下的模块。

## 开发工作流

### AI Coding 协作流程

1. **Spec → Plan → Tasks**: 每个功能模块 MUST 先通过 `/speckit-specify` 生成 spec，
   再通过 `/speckit-plan` 生成实施计划，最后通过 `/speckit-tasks` 拆分为任务列表。
2. **AI 生成代码**: 每个 task 由 Claude Code 生成，生成后 MUST 通过
   `/speckit-implement` 验证可运行。
3. **人工 Review**: AI 生成的代码 MUST 经过人工确认，重点检查 Agent 编排逻辑、
   Mock 数据的业务合理性和 UI 交互流程。
4. **录制演示**: 每完成一个业务场景的开发，录制演示视频，截取关键界面。

### 质量门禁

- 所有 Mock 函数 MUST 可通过简单的调用测试验证。
- Agent 图 MUST 可在无 LLM 环境下通过模拟输出来验证图的拓扑结构。
- 前端三栏布局 MUST 在 1920×1080 分辨率下正常展示。
- 每个场景的完整流程 MUST 可手动走通至少一次。

## Governance

### 修订流程

1. 任何原则的修改 MUST 通过修改本宪法文件并更新版本号来完成。
2. MAJOR 版本升级（如移除或重新定义核心原则）MUST 附带迁移计划说明。
3. MINOR 版本升级（新增原则或章节）MUST 更新 Sync Impact Report。
4. PATCH 版本升级（措辞澄清、错字修正）可直接提交。

### 版本策略

- 遵循 MAJOR.MINOR.PATCH 语义化版本。
- 版本号存储在本文件底部的 Version 字段。
- 每次修订 MUST 同步更新 Last Amended 日期。

### 合规审查

- 每个 spec、plan、tasks 文档 MUST 在生成时通过 Constitution Check 自检。
- 发现与宪法冲突的实现 MUST 在 plan.md 的 Complexity Tracking 中记录并说明理由。
- 架构选型如偏离 LangGraph / Streamlit，MUST 在 plan.md 中提供充分论证。

**Version**: 2.0.0 | **Ratified**: 2026-06-09 | **Last Amended**: 2026-06-13
