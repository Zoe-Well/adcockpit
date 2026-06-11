<!--
Sync Impact Report
==================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: N/A (first version)
Added sections:
  - Core Principles (5 principles, user-specified)
  - 技术约束 (Technical Constraints)
  - 开发工作流 (Development Workflow)
  - Governance
Removed sections: None
Templates requiring updates:
  ✅ plan-template.md — "Constitution Check" section is dynamically gated; no static changes needed
  ✅ spec-template.md — generic placeholders align with business domains; no changes needed
  ✅ tasks-template.md — generic task phases align with AI-First workflow; no changes needed
  ✅ checklist-template.md — generic; no changes needed
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

### IV. AI-First 开发范式

项目代码 MUST 由 AI Coding 生成不低于 95%，前端 MUST 优先使用 Streamlit 构建。

- 所有 Agent 节点、Mock 工具、前端组件均由 Claude Code 等 AI 工具生成。
- 前端选用 Streamlit 作为首选框架，通过 WebSocket 实时推送执行状态。
- 后端采用 FastAPI，Agent 编排层使用 LangGraph。
- LLM 层支持 deepseek，通过 Function Calling 驱动工具调用。
- 项目结构遵循：`agents/` (Agent 定义)、`tools/` (Mock 函数)、`ui/` (Streamlit
  三栏布局)、`api/` (FastAPI 后端)。

**理由**: 演示目标之一是展示 AI Coding 工作流能力。Streamlit 提供最快的 UI 原型
速度，适合 Demo 场景。95% AI 生成率是自我验证 AI Coding 范式的硬指标。

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

## 技术约束
## 技术栈约束
## 1. 强制性版本约束 (Hard Constraints)
| 类别 | 强制约束 (Must Use) | 补充要求/目标 |
| :--- | :--- | :--- |
| **语言/运行时** | **Python 3.11** | 必须使用现代语法特性。 |
| **API 框架** | **FastAPI==0.136.3** | 所有API定义必须使用Pydantic模型。 |
| **ASGI 服务器** | **uvicorn[standard]==0.49.0** | 用于运行FastAPI应用。 |
| **核心 Agent 框架** | **LangGraph==1.0.10** | **禁止**使用 `create_react_agent`，必须使用新的函数式API。 |
| **LLM 集成库** | **LangChain==1.2.3** | **必须**通过 `create_agent` 和中间件构建Agent。 |
| **LLM 接口库** | **langchain-openai==1.0.1** | 用于通过统一接口调用GLM-4模型。 |
| **工具定义** | **LangChain Tools (@tool)** | 所有Agent工具必须用此方式定义。 |
| **状态管理** | **LangGraph 内置 MemorySaver** | 用于管理会话状态和记忆。 |
| **API 集成** | **FastAPI Mock Server** | 模拟巨量引擎API，代码需易于替换为真实调用。 |
| **包管理工具** | **uv** | 统一使用uv进行依赖管理和虚拟环境管理。 |
| **环境变量管理** | **python-dotenv==1.0.0** | 用于加载`.env`文件中的配置。 |

## 2. 版本选择理由 (Rationale for Version Locking)
- **LangGraph 1.0+**：提供了更稳定、类型安全的函数式API（`@entrypoint`, `@task`），是未来发展的方向，可避免使用已废弃的API。
- **LangChain 1.0+**：与LangGraph 1.0同步发布，提供了更模块化的架构和统一的Agent构建方式（`create_agent`）。

**依赖管理**:
- MUST 使用 `requirements.txt` 或 `pyproject.toml` 管理依赖
- 依赖版本 MUST 锁定主要版本号（如 `fastapi>=0.100.0,<1.0.0`）

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

**Version**: 1.0.0 | **Ratified**: 2026-06-09 | **Last Amended**: 2026-06-09
