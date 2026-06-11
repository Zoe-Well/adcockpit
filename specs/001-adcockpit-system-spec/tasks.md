# Tasks: AdCockpit 数字营销 AI Agent 系统

**Input**: Design documents from `specs/001-adcockpit-system-spec/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included — pytest scenario tests for all 5 user stories

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and base structure

- [ ] **T001** 创建项目目录结构：按照 plan.md 定义创建 `agents/`、`tools/`、`api/`、`ui/panels/`、`ui/components/`、`tests/unit/`、`tests/scenarios/` 全部目录和 `__init__.py` 文件。
  > **推荐提示词**: "在项目根目录创建以下 Python 包目录结构，每个目录包含空白 `__init__.py`：`agents/`、`tools/`、`api/`、`ui/`、`ui/panels/`、`ui/components/`、`tests/`、`tests/unit/`、`tests/scenarios/`。参考 `specs/001-adcockpit-system-spec/plan.md` 中的 Source Code 目录树。"

- [ ] **T002** 生成 `requirements.txt`：包含 fastapi>=0.110、uvicorn>=0.27、langgraph>=0.2、langchain>=0.2、langchain-openai>=0.1、streamlit>=1.28、sse-starlette>=2.0、pytest>=8.0、pytest-asyncio>=0.23、httpx>=0.27、python-dotenv>=1.0。
  > **推荐提示词**: "生成 `requirements.txt`，包含以下依赖：fastapi>=0.110, uvicorn>=0.27, langgraph>=0.2, langchain>=0.2, langchain-openai>=0.1, streamlit>=1.28, sse-starlette>=2.0, pytest>=8.0, pytest-asyncio>=0.23, httpx>=0.27, python-dotenv>=1.0。每行一个依赖。"

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] **T003** 定义 AgentState TypedDict 及子类型在 `agents/state.py`：实现 `TaskNode`、`PlatformData`、`StrategyAction`、`ExecutionResult`、`AgentState` 五个 TypedDict，字段与 spec.md 中 State 定义完全一致。
  > **推荐提示词**: "在 `agents/state.py` 中定义 TypedDict `AgentState`，包含字段 `user_input: str`, `task_graph: List[TaskNode]`, `platform_data: List[PlatformData]`, `analysis_result: Dict[str, Any]`, `strategy_actions: List[StrategyAction]`, `execution_results: List[ExecutionResult]`, `report: Dict[str, Any]`, `pending_approval: Optional[List[StrategyAction]]`, `conversation_history: List[Dict[str, str]]`, `error_log: List[Dict[str, Any]]`, `session_id: str`, `current_scene: Literal['ad_placement','content','ecommerce','data_analysis','diagnosis']`。同时定义子 TypedDict：TaskNode(id, type, platform, params, depends_on, status), PlatformData(platform, endpoint, data, fetched_at, error), StrategyAction(target_id, target_type, action, params, risk_level, expected_effect, requires_approval), ExecutionResult(action, status, response, error, retry_count, executed_at)。所有字段参考 `specs/001-adcockpit-system-spec/spec.md` 中的 State 定义部分。"

- [ ] **T004** 创建 Mock 数据常量文件 `tools/mock_data.py`：定义 `DOUYIN_PLANS`（C001-C005，ROI 分别为 1.5/2.3/3.1/1.8/2.5）、`TENCENT_PLANS`（T001-T005，ROI 分别为 1.2/2.8/3.5/2.1/2.6）、`CREATIVES`（6 条素材）、`PRODUCTS`（2 个商品）、`CLIENT_DATA`（5 个客户），所有数值必须与 `adcockpit-prototype.html` 中展示的数据完全一致。
  > **推荐提示词**: "在 `tools/mock_data.py` 中定义以下 Mock 数据常量，**数值必须与 `adcockpit-prototype.html` 中的假数据完全一致**：\n1. DOUYIN_PLANS：5 条计划，[{id:'C001',name:'夏季促销-A',cost:15200,roi:1.5,bid:25.0,status:'active',ctr:0.035,cvr:0.038}, {id:'C002',name:'新品首发-B',cost:14100,roi:2.3,bid:30.0,status:'active',ctr:0.042,cvr:0.045}, {id:'C003',name:'爆款返场-C',cost:12800,roi:3.1,bid:22.0,status:'active',ctr:0.051,cvr:0.052}, {id:'C004',name:'品牌日-D',cost:9600,roi:1.8,bid:20.0,status:'active',ctr:0.033,cvr:0.036}, {id:'C005',name:'直播引流-E',cost:8800,roi:2.5,bid:18.0,status:'active',ctr:0.040,cvr:0.043}]\n2. TENCENT_PLANS：5 条计划，[{id:'T001',name:'618大促',cost:12800,roi:1.2,bid:30.0,status:'active',ctr:0.028,cvr:0.031}, {id:'T002',name:'会员日',cost:11000,roi:2.8,bid:28.0,status:'active',ctr:0.045,cvr:0.048}, {id:'T003',name:'达人种草',cost:9500,roi:3.5,bid:24.0,status:'active',ctr:0.055,cvr:0.058}, {id:'T004',name:'品宣视频',cost:8200,roi:2.1,bid:21.0,status:'active',ctr:0.038,cvr:0.040}, {id:'T005',name:'直播切片',cost:7600,roi:2.6,bid:19.0,status:'active',ctr:0.043,cvr:0.046}]\n3. CREATIVES：6 条素材（高 CTR 3 条 + 低 CTR 3 条），包含 id, platform, name, type, url(mock), ctr, completion_rate, created_at\n4. PRODUCTS：2 个商品 [{id:'A',name:'爆款T恤',stock:32,reserved:10,price:99.0,status:'low_stock'}, {id:'B',name:'新品连衣裙',stock:200,reserved:0,price:199.0,status:'on_sale'}]\n5. CLIENT_DATA：5 个客户 [{name:'客户A',platforms:{douyin:{cost:25000,roi:1.5,cpa:40},tencent:{cost:15000,roi:1.3,cpa:45},xiaohongshu:{cost:10000,roi:1.8,cpa:35}}}, ...]"

- [ ] **T005** [P] 实现 24 个 Mock 函数在 `tools/mock_functions.py`：按广告投放/内容生产/电商闭环/数据分析/通知推送五大域分组。每个函数从 `mock_data.py` 读取种子数据，使用 `random.random()` 以 10% 概率抛业务异常、5% 概率抛网络异常、85% 概率正常返回。包含完整 Google-style docstring。
  > **推荐提示词**: "在 `tools/mock_functions.py` 中实现 24 个 Mock 函数。每个函数：(1) 从 `tools.mock_data` 导入对应的种子数据，(2) 使用 `random.random()` 以 10% 概率抛出业务异常(如 `ReviewRejected('素材审核拒绝')`, `InsufficientBalance('账户余额不足')`)，5% 概率抛出网络异常(如 `TimeoutError('请求超时')`, `ConnectionError('服务不可用')`)，(3) 85% 概率返回与原型一致的正常响应，(4) 添加 `time.sleep(random.uniform(0.1, 2.0))` 模拟网络延迟。函数清单：\n广告投放域(8)：get_top_campaigns, get_campaign_detail, update_bid, update_budget, get_plan_status, replace_creative, resubmit_plan, get_platform_report\n内容生产域(4)：get_top_creatives, analyze_video_frames, generate_script, publish_to_feishu\n电商闭环域(5)：get_product_stock, update_stock, create_coupon, get_live_metrics, send_live_script\n数据分析域(3)：get_multi_platform_report, generate_budget_proposal, generate_ppt_outline\n通知系统域(4)：send_feishu_notification, log_to_erp, save_user_preference, load_user_preference\n每个函数包含完整 Google-style docstring（Args, Returns, Raises）。get_top_campaigns('douyin',...) 必须返回与 DOUYIN_PLANS 一致的数据。"

- [ ] **T006** [P] 创建工具注册表 `tools/tool_registry.py`：将 24 个 Mock 函数封装为 LangChain `StructuredTool`，按域名分组为 `AD_TOOLS`、`CONTENT_TOOLS`、`ECOM_TOOLS`、`DATA_TOOLS`、`NOTIFY_TOOLS`、`ALL_TOOLS` 六个列表，供 Agent 节点通过 Function Calling 调用。
  > **推荐提示词**: "在 `tools/tool_registry.py` 中为 24 个 Mock 函数创建 LangChain StructuredTool 注册表。从 `tools.mock_functions` 导入所有函数，每个函数用 `StructuredTool.from_function()` 封装，定义 `name`、`description`、`args_schema`(Pydantic model)。按域分组为列表：AD_TOOLS(8个), CONTENT_TOOLS(4个), ECOM_TOOLS(5个), DATA_TOOLS(3个), NOTIFY_TOOLS(4个), ALL_TOOLS(全部24个)。导出这些列表供 Agent 节点使用。"

- [ ] **T007** 实现 SSE Manager `api/sse_manager.py`：`SSEManager` 类，维护 `asyncio.Queue` per session，提供 `create_session()`、`emit(session_id, event_type, data)`、`stream(session_id)` async generator。支持六种事件类型：`step_start`、`step_update`、`step_complete`、`approval_required`、`step_error`、`execution_complete`，数据格式与 `contracts/api-contracts.md` 中 SSE 事件定义一致。
  > **推荐提示词**: "在 `api/sse_manager.py` 中实现 SSEManager 类。功能：(1) `create_session(session_id: str)` 创建一个 asyncio.Queue 作为该 session 的事件队列，(2) `async emit(session_id, event_type, data)` 向队列推送 `{event, data}` 格式的消息，(3) `async stream(session_id)` 返回 async generator，从队列中逐条 yield SSE 格式字符串 `'event: {event_type}\\ndata: {json}\\n\\n'`，(4) 支持事件类型：step_start/step_update/step_complete/approval_required/step_error/execution_complete，(5) `disconnect(session_id)` 清理队列。事件数据格式参考 `specs/001-adcockpit-system-spec/contracts/api-contracts.md` 中 SSE Event Stream 部分。"

- [ ] **T008** 实现 FastAPI 主入口和路由 `api/main.py` + `api/routes.py`：FastAPI app 配置 CORS，挂载 SSE 端点，定义 `POST /execute`（触发 LangGraph 图执行 + SSE 流式推送）、`POST /approve/{session_id}`（恢复执行）、`POST /reject/{session_id}`（取消执行）、`GET /session/{session_id}/state`（查询状态）、`GET /stream/{session_id}`（SSE 流）。
  > **推荐提示词**: "创建 `api/main.py` 和 `api/routes.py`。在 `main.py` 中：(1) 创建 FastAPI app，(2) 配置 CORS middleware 允许 localhost:8501（Streamlit 默认端口），(3) 包含 `from api.routes import router` 并 `app.include_router(router)`，(4) 添加 startup 事件创建 SSEManager 实例存储在 app.state。在 `routes.py` 中定义路由：\n- `POST /execute`：接收 `{user_input, session_id}`，创建 LangGraph 图配置(config with session_id)，使用 `graph.astream_events(state, config, version='v2')` 流式执行，每个 on_chain_start/end 事件通过 sse_manager.emit() 推送，捕获 NodeInterrupt 时推送 approval_required 事件并等待外部 resume，返回 `{session_id, status, current_scene}`\n- `POST /approve/{session_id}`：通过 `Command(resume={'approved': True})` 恢复图执行\n- `POST /reject/{session_id}`：通过 `Command(resume={'approved': False})` 恢复图执行\n- `GET /session/{session_id}/state`：从 MemorySaver checkpointer 读取并返回当前状态快照\n- `GET /stream/{session_id}`：返回 `StreamingResponse(sse_manager.stream(session_id), media_type='text/event-stream')`\n使用依赖注入获取 app.state.sse_manager。"

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — 跨平台广告投放智能优化 (Priority: P1) 🎯 MVP

**Goal**: 用户输入投放优化指令 → Supervisor 拆解 → Data 并行拉取抖音+腾讯 →
Analysis 筛选 ROI<2 → Strategy 生成调价策略 → 人工确认 → Execute 执行 →
Report 生成报告。完整链路在三栏 UI 中可视化展示。

**Independent Test**: 在前端输入"检查最近7天抖音和腾讯广告Top5消耗计划中ROI<2的，
自动降价10%并生成报告"，验证中间面板展示完整步骤流（含并行 Data Agent 步骤），
右侧仪表盘显示 ROI 指标/柱状图/告警/报告，左侧弹出确认卡片，确认后执行完成。

### Tests for User Story 1

- [ ] **T009** [P] [US1] 创建场景 1 集成测试 `tests/scenarios/test_scenario_1_ad_placement.py`：验证投放优化全链路 SSE 事件顺序（supervisor→data_agent(douyin+tencent并行)→analysis→strategy→approval_required→execute→report→execution_complete），验证 Mock 数据与原型一致（C001 ROI=1.5, T001 ROI=1.2），验证 approval 包含 4 条 action，验证最终 report 的 estimated_saving='15%' 和 roi_improvement='2.1'。
  > **推荐提示词**: "在 `tests/scenarios/test_scenario_1_ad_placement.py` 中实现投放优化场景端到端 pytest 测试。使用 `tests/conftest.py` 中的 fixtures (test_client, mock_llm, sse_collector)。测试函数 `test_ad_placement_full_flow`：(1) POST /execute 发送投放优化指令 '检查最近7天在抖音和腾讯广告上，消耗排名Top5的计划里哪些ROI低于2，对不达标的计划自动降价10%'，(2) 收集 SSE 事件到列表，(3) 验证事件顺序为 supervisor→data_agent→analysis_agent→strategy_agent→approval_required，(4) 验证 approval_required 的 actions 包含 4 条策略（C001 降价10%, T001 降价10%, T001 降预算20%, C004 降价10%），(5) POST /approve 发送确认，(6) 验证后续事件 execute_agent→report_agent→execution_complete，(7) 验证 report 中 estimated_saving='15%', estimated_roi_improvement='2.1'，(8) 验证 data_agent 返回的 douyin plans 中 C001.roi=1.5, C004.roi=1.8。另写 `test_data_consistency_with_prototype` 验证 get_top_campaigns 返回数据与 adcockpit-prototype.html 中展示完全一致。使用 pytest-asyncio 标记。"

### Implementation for User Story 1

- [ ] **T010** [P] [US1] 实现 Supervisor Agent 在 `agents/supervisor.py`：使用 LLM 解析用户输入，识别场景为 `ad_placement`，拆解 task_graph 为 6 个子任务（T1 拉取抖音、T2 拉取腾讯、T3 合并分析、T4 生成策略、T5 执行操作、T6 生成报告），T1/T2 标记为并行，T5 标记 requires_approval=True。
  > **推荐提示词**: "在 `agents/supervisor.py` 中实现 `supervisor_node(state: AgentState) -> dict` 函数。使用 LLM（通过 ChatOpenAI/ChatAnthropic）分析 `state['user_input']`：\n(1) 提取关键词识别场景类型：包含'ROI/调价/计划/消耗'→'ad_placement'，'素材/脚本/视频/内容'→'content'，'直播/库存/优惠券/场控'→'ecommerce'，'报表/分析/预算/客户'→'data_analysis'，'排查/诊断/故障/没量'→'diagnosis'\n(2) 根据场景生成 task_graph：投放场景固定为 6 个子任务 [{id:'T1',type:'fetch_data',platform:'douyin',params:{metric:'cost',top_n:5,days:7},depends_on:[],status:'pending'}, {id:'T2',type:'fetch_data',platform:'tencent',params:{metric:'cost',top_n:5,days:7},depends_on:[],status:'pending'}, {id:'T3',type:'analyze',params:{filter:'roi<2'},depends_on:['T1','T2'],status:'pending'}, {id:'T4',type:'strategize',depends_on:['T3'],status:'pending'}, {id:'T5',type:'execute',params:{requires_approval:true},depends_on:['T4'],status:'pending'}, {id:'T6',type:'report',depends_on:['T5'],status:'pending'}]\n(3) 设置 current_scene 为识别的场景类型\n(4) 保留原有 conversation_history，追加 user message\n返回 {**state, 'task_graph':..., 'current_scene':..., 'conversation_history':...}"

- [ ] **T011** [P] [US1] 实现 Data Agent 在 `agents/data_agent.py`：根据 task_graph 中间类型为 `fetch_data` 的节点，并行调用对应平台的 `get_top_campaigns` Mock 函数。将返回结果封装为 `PlatformData` 并 append 到 `state['platform_data']`。更新 task 状态为 done/failed。
  > **推荐提示词**: "在 `agents/data_agent.py` 中实现 `data_agent_node(state: AgentState) -> dict` 函数。逻辑：(1) 从 task_graph 中筛选 type='fetch_data' 且 status='pending' 的任务，(2) 按 platform 分组，使用 `asyncio.gather` 并行调用 `tools.mock_functions.get_top_campaigns(platform, **params)`，(3) 将每个结果封装为 PlatformData(platform=..., endpoint='get_top_campaigns', data=[...], fetched_at=datetime.now().isoformat(), error=None)，append 到 state['platform_data']，(4) 更新对应 task 的 status 为 'done'，(5) 异常时 status='failed' 并记录到 error_log，但继续处理其他任务。返回更新后的 state dict。注意先用 `concurrent.futures.ThreadPoolExecutor` 包装 sync mock 函数以支持 asyncio。"

- [ ] **T012** [US1] 实现 Analysis Agent 在 `agents/analysis_agent.py`：合并 platform_data，筛选 ROI<2 的计划，输出 `analysis_result` 包含 anomalies 列表（含 plan_id、platform、cost、roi、severity、trend）和 summary 文本。投放场景的 severity 判定：roi<1.5→critical, roi<2.0→high, roi<2.3→medium。
  > **推荐提示词**: "在 `agents/analysis_agent.py` 中实现 `analysis_agent_node(state: AgentState) -> dict` 函数。投放场景逻辑：(1) 从 platform_data 中提取所有 plans 并合并为 flat list，(2) 筛选 roi < 2.0 的计划，(3) 对每个异常计划判定 severity：roi < 1.2 → 'critical'，roi < 1.5 → 'high'，roi < 2.0 → 'medium'，(4) 计算 trend（对比 mock 历史数据或标记为'declining'/'flat'），(5) 填充 analysis_result = {anomalies: [{plan_id, platform, cost, roi, severity, trend}], summary: '3/10 计划 ROI 低于目标值 2.0，总不达标消耗占比 37.6%', total_analyzed: 10}，(6) 更新 task_graph 中 T3 状态为 done。返回更新后的 state。投放场景中 analysis_result 的 anomalies 必须包含 C001(roi 1.5/high)、T001(roi 1.2/critical)、C004(roi 1.8/medium)。"

- [ ] **T013** [US1] 实现 Strategy Agent 在 `agents/strategy_agent.py`：基于 analysis_result 中的 anomalies，生成 `StrategyAction` 列表。每条 action 包含 target_id、action、params、risk_level、expected_effect、requires_approval。投放场景中：roi<2 的计划降价 10%（low/medium risk），roi<1.5 的额外降预算 20%（high risk，requires_approval=True）。
  > **推荐提示词**: "在 `agents/strategy_agent.py` 中实现 `strategy_agent_node(state: AgentState) -> dict` 函数。投放场景逻辑：遍历 analysis_result['anomalies']，对每个异常计划生成策略：(1) 所有 ROI<2 计划：action='update_bid', params={new_bid: current_bid*0.9}, risk_level='medium', expected_effect=f'ROI提升至{roi*1.2:.1f}', requires_approval=True，(2) ROI<1.5 的额外生成：action='update_budget', params={new_budget: current_budget*0.8}, risk_level='high', requires_approval=True，(3) ROI 在 1.5-2.0 之间仅降价，risk_level='low'。生成的 actions 必须包含 4 条：(C001,update_bid,22.5,medium), (T001,update_bid,27.0,medium), (T001,update_budget,4000,high), (C004,update_bid,18.0,low)。附加 estimated_saving='15%' 和 estimated_roi_improvement='2.1' 到 analysis_result。设置 state['strategy_actions'] = actions。更新 T4 状态。"

- [ ] **T014** [US1] 实现 Execute Agent 在 `agents/execute_agent.py`：遍历 `strategy_actions`，检查 `requires_approval` 标志——若 True 则将 actions 放入 `pending_approval` 并调用 LangGraph `interrupt()` 暂停图执行；若 False 则直接执行对应的 Mock 函数（如 `update_bid`）。执行后填充 `execution_results`，失败自动重试最多 3 次。
  > **推荐提示词**: "在 `agents/execute_agent.py` 中实现 `execute_agent_node(state: AgentState) -> dict` 函数。逻辑：(1) 检查 strategy_actions 中是否有 requires_approval=True 的 action，(2) 如果有，将所有待审批 actions 放入 `state['pending_approval']`，然后调用 `from langgraph.types import interrupt` 的 `interrupt(state['pending_approval'])` 暂停图，(3) 当通过 Command(resume={'approved': True}) 恢复时，遍历 actions 并行执行对应 Mock 函数（通过 action.action 名称查找 `tools.mock_functions` 中的函数），(4) 每次执行结果记录到 execution_results：ExecutionResult(action=..., status='success'|'failed', response=..., error=..., retry_count=..., executed_at=...)，(5) 失败时最多重试 3 次，每次重试前等待 1s，(6) 所有执行完成后更新 T5 状态为 done。当 resume={'approved': False} 时，将 actions 标记为 status='cancelled'。返回更新后的 state。"

- [ ] **T015** [US1] 实现 Report Agent 在 `agents/report_agent.py`：聚合所有 execution_results 和 analysis_result，生成结构化报告 `report` 字典。包含：title（如"今日投放优化报告"）、summary 要点列表、actions_taken、estimated_saving、estimated_roi_improvement、generated_at。
  > **推荐提示词**: "在 `agents/report_agent.py` 中实现 `report_agent_node(state: AgentState) -> dict` 函数。聚合所有上游输出生成报告：(1) 从 analysis_result 取 anomalies 和 summary，(2) 从 execution_results 取执行结果统计（成功/失败/取消数量），(3) 从 strategy_actions 取 estimated_saving 和 estimated_roi_improvement，(4) 生成 report = {title: '今日投放优化报告', scene: state['current_scene'], summary: ['分析计划数: 10 条（抖音 5 + 腾讯 5）', '不达标计划: 3 条（ROI < 2.0）', f'预计节省消耗: ¥{total_cost*estimated_saving_pct:.0f}/天（{estimated_saving_pct*100:.0f}%）', f'预计 ROI 提升: {current_roi} → {target_roi}'], actions_taken: len(成功), recommendations: ['持续监控调价后 ROI 变化', '关注 T001 计划素材审核状态'], generated_at: datetime.now().isoformat()}，(5) 更新 T6 状态为 done。投放场景的 estimated_saving='15%' (¥5,640)，roi_improvement='1.87→2.1'。"

- [ ] **T016** [US1] 构建 LangGraph StateGraph 在 `agents/graph.py`：定义完整的有向图，节点为 supervisor→data_agent→analysis_agent→route_after_analysis→strategy_agent→execute_agent→report_agent，`route_after_analysis` 根据 `current_scene` 条件路由。使用 MemorySaver 作为 checkpointer，编译导出 `app` 实例。
  > **推荐提示词**: "在 `agents/graph.py` 中构建并编译 LangGraph StateGraph。步骤：(1) 从各 agent 模块导入节点函数（supervisor_node, data_agent_node, analysis_agent_node, strategy_agent_node, content_agent_node, ecommerce_agent_node, execute_agent_node, report_agent_node），(2) 创建 StateGraph(AgentState)，(3) 添加节点：add_node('supervisor', supervisor_node), add_node('data_agent', data_agent_node), add_node('analysis_agent', analysis_agent_node), add_node('strategy_agent', strategy_agent_node), add_node('content_agent', content_agent_node), add_node('ecommerce_agent', ecommerce_agent_node), add_node('execute_agent', execute_agent_node), add_node('report_agent', report_agent_node)，(4) 添加边：START→supervisor, supervisor→data_agent, data_agent→analysis_agent，(5) 添加条件边：analysis_agent→route_after_analysis（函数检查 current_scene: ad_placement/data_analysis→strategy_agent, content→content_agent, ecommerce→ecommerce_agent），(6) strategy_agent/content_agent/ecommerce_agent→execute_agent, execute_agent→report_agent, report_agent→END，(7) 编译：`graph.compile(checkpointer=MemorySaver(), interrupt_before=['execute_agent'])`（在 execute_agent 前允许 interrupt），(8) 导出 compiled graph 为模块级变量 `app`。"

- [ ] **T017** [US1] 实现 Streamlit 主题 CSS 注入 `ui/theme.py`：注入与 `adcockpit-prototype.html` 完全一致的 CSS 变量、全局样式、动画、滚动条样式，隐藏 Streamlit 默认 header/footer/menu。
  > **推荐提示词**: "在 `ui/theme.py` 中实现 `inject_custom_css()` 函数。使用 `st.markdown('<style>...</style>', unsafe_allow_html=True)` 注入与 `adcockpit-prototype.html` 中完全相同的 CSS。必须包含：\n1. CSS 变量：--bg-primary:#0f1117, --bg-secondary:#1a1d27, --bg-tertiary:#242836, --border:#2a2e3a, --text-primary:#e8eaed, --text-secondary:#9aa0b0, --text-muted:#5f6570, --accent:#4c6ef5, --success:#51cf66, --warning:#fcc419, --danger:#ff6b6b, --info:#22b8cf\n2. 全局样式：body font-family(-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif), bg var(--bg-primary), color var(--text-primary), overflow hidden\n3. 隐藏 Streamlit 元素：header{visibility:hidden}, footer{visibility:hidden}, #MainMenu{visibility:hidden}, .stDeployButton{display:none}\n4. 动画：@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}, slideIn{from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}}, spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}\n5. Scrollbar：::-webkit-scrollbar{width:5px}, track transparent, thumb: var(--border)\n6. Streamlit column gap: .stHorizontalBlock{gap:0!important}\n直接复制 `adcockpit-prototype.html` 中 <style> 标签内的全部内容，但移除 HTML 元素选择器，只保留全局和可复用的 CSS。"

- [ ] **T018** [US1] 实现 Streamlit 主入口 `ui/app.py`：三栏布局 `st.columns([0.25,0.40,0.35])`。初始化 session_state（trace_events、chat_messages 含预置欢迎语、approval_pending、current_scene、session_id）。后台线程通过 `httpx` 连接 FastAPI `/stream/{sid}` SSE 端点，将事件写入 `trace_events`。使用 `time.sleep(0.5)` + `st.rerun()` 轮询模式驱动实时更新。
  > **推荐提示词**: "在 `ui/app.py` 中实现 AdCockpit Streamlit 主页面。步骤：\n1. `st.set_page_config(layout='wide', page_title='AdCockpit', page_icon='⚡')`\n2. 调用 `inject_custom_css()` 注入主题\n3. 初始化 session_state：session_id=f\"demo-{datetime.now().strftime('%m%d-%H%M')}\", trace_events=[], chat_messages=[{role:'agent', content:'👋 你好，我是 AdCockpit AI 优化师…(与原型一致)'}], approval_pending=None, current_scene='ad_placement', dashboard_data={}, sse_connected=False\n4. 顶部栏：st.markdown HTML 渲染 Logo、场景标签、系统状态灯、Session ID\n5. 场景标签：st.columns(5) 渲染 5 个按钮('📊 投放优化'/'🎬 内容生产'/'🛒 电商场控'/'📈 数据分析'/'🔧 故障诊断')，点击更新 current_scene\n6. 三栏：left,center,right = st.columns([0.25,0.40,0.35])\n7. 启动后台线程（使用 threading.Thread + daemon=True）：通过 httpx.AsyncClient 连接 `http://localhost:8000/stream/{session_id}` SSE 端点，解析每行 'data: {...}' JSON 并 append 到 st.session_state.trace_events，设置 sse_connected=True\n8. 各栏调用对应 panel 渲染函数：left→render_chat_panel(), center→render_trace_board(), right→render_dashboard()\n9. 轮询机制：在页面末尾使用 st.empty() placeholder + time.sleep(0.5) + st.rerun() 实现 ~2fps 的实时刷新"

- [ ] **T019** [P] [US1] 实现 ChatPanel 组件 `ui/panels/chat_panel.py`：渲染对话消息列表（user 右对齐蓝底+王头像，agent 左对齐暗底+AI头像，配套 CSS class）。条件渲染 ApprovalCard（当 `pending_approval` 非空时在消息列表底部渲染，展示每条 action 的目标/操作/风险标签）。底部固定输入框+发送按钮，支持回车发送。场景标签更新输入框占位符。
  > **推荐提示词**: "在 `ui/panels/chat_panel.py` 中实现 `render_chat_panel()` 函数。复刻 `adcockpit-prototype.html` 左侧面板：(1) 场景快捷标签 row：st.columns(5) 渲染 5 个标签按钮，active 标签高亮蓝色边框，(2) 消息列表：遍历 st.session_state.chat_messages，每条消息渲染 st.markdown HTML：user 消息→`.chat-msg.user` 右对齐，`.avatar` 显示'王'，`.bubble` 蓝底白字 border-top-right-radius:4px；agent 消息→`.chat-msg.agent` 左对齐，`.avatar` 显示'AI'蓝底白字，`.bubble` 暗底白字 border-top-left-radius:4px，(3) ApprovalCard 条件渲染：当 st.session_state.pending_approval 非空时，渲染 `.approval-card` HTML，遍历每条 action 显示 `.ac-row`(目标/操作/风险标签颜色)，底部两个按钮 st.columns(2)：'✅ 确认执行'（调用 POST /approve）和'✕ 取消'（调用 POST /reject），点击后更新 pending_approval=None，(4) 输入区域：st.text_input + st.button('发送 ➤')，回车或点击发送时调用 POST /execute，将用户消息追加到 chat_messages。所有样式 class 名称与原型一致。"

- [ ] **T020** [P] [US1] 实现 TraceBoard 组件 `ui/panels/trace_board.py`：渲染 DAG 任务栏（Supervisor→Data⇉Data→Analysis→Strategy→Execute→Report 节点链，用原型 `.dag-node` 颜色）。从 `trace_events` 驱动步骤卡片列表（StepCard），每张卡片含状态图标（✅/🔄/⏸️/❌/⏳）、标题（Agent名+操作+耗时）、描述、可展开工具调用 JSON 详情。失败卡片显示重试按钮。
  > **推荐提示词**: "在 `ui/panels/trace_board.py` 中实现 `render_trace_board()` 函数。复刻 `adcockpit-prototype.html` 中间面板：(1) DAG 任务栏：st.markdown HTML 渲染节点链 `<span class='dag-node supervisor'>🧠 Supervisor</span> <span class='dag-arrow'>→</span> <span class='dag-node data'>📡 Data</span> <span class='dag-arrow'>⇉</span> <span class='dag-node data'>📡 Data</span> <span class='dag-arrow'>→</span> ...`，各节点使用原型 .dag-node.{supervisor=rgba(76,110,245,0.2)蓝, data=rgba(34,184,207,0.2)青, analysis=rgba(252,196,25,0.2)黄, strategy=rgba(132,94,247,0.2)紫, execute=rgba(81,207,102,0.2)绿, report=rgba(255,107,107,0.2)红}，(2) 从 st.session_state.trace_events 构建步骤卡片列表：去重合并同一 node 的 start/update/complete 事件，推导当前 status，(3) 每张卡片 st.markdown HTML：外层 `.step-card.status-{status}`（左边框颜色 done=绿 running=蓝 waiting=黄 failed=红 pending=灰半透明），内层 `.step-icon.{status}`（done=✅ running=🔄span.spin waiting=⏸️ failed=❌ pending=⏳），`.step-title`（Agent名+tool名+耗时），`.step-desc`（描述文本），可展开 `.tool-call`（默认折叠，点击展开显示 Request/Response JSON pre 标签），失败时显示 `<button class='retry-btn'>重试</button>`"

- [ ] **T021** [P] [US1] 实现 InsightDashboard 组件 `ui/panels/dashboard.py`：场景路由器，根据 `current_scene` 切换子视图。投放场景 `AdDashboard`：6 个 MetricCard（ROI 1.87 红框/消耗 ¥37,600/CPA ¥38.5/活跃 10/CTR 3.8%/CVR 4.2%）、ROI 柱状图（10 条计划，<2.0 红色+虚线阈值线）、3 条异常告警、优化报告预览（一键复制）。
  > **推荐提示词**: "在 `ui/panels/dashboard.py` 中实现 `render_dashboard()` 函数。使用场景路由器：if current_scene=='ad_placement'→AdDashboard, 'content'→ContentDashboard, 'ecommerce'→EcommerceDashboard, 'data_analysis'→DataDashboard, 'diagnosis'→DiagnosisDashboard。\n\nAdDashboard：(1) 6 个 MetricCard 2列网格：st.columns(2)×3 行渲染，数据：ROI 1.87(highlight红框+down▼0.23), 总消耗 ¥37,600(up▲8.5%), 平均CPA ¥38.5(warn≈持平), 活跃计划 10(up 3条需关注), CTR 3.8%(up▲0.4%), CVR 4.2%(down▼0.3%)，(2) ROI 柱状图：st.markdown HTML 渲染 10 根柱状 `.chart-bar`，高度=roi/max_roi*110px，roi<2.0 用 `.chart-bar.low` 红色渐变，显示数值在柱顶+计划名在底部，2.0 处 dashed 红色阈值线，(3) 异常告警列表：3条(T001🔴'ROI严重偏低'/C001🟠'ROI持续下滑'/C004🟡'ROI略低于阈值')，左边框颜色对应，(4) 报告预览：st.markdown HTML 渲染 `.report-summary`，7行指标(分析计划数10/不达标3/建议调价3/降预算1/节省¥5,640/ROI→2.1)+st.button('📋 一键复制报告')调用 pyperclip.copy()。\n\n确保所有数值与 `adcockpit-prototype.html` 完全一致。"

- [ ] **T022** [P] [US1] 实现 MetricCard 组件 `ui/components/metric_card.py`：可复用函数 `metric_card(label, value, sub_text, sub_trend, highlight=False)`，渲染带原型 `.metric-card` 样式的 HTML 卡片，sub_trend='up'→绿色、'down'→红色、'warn'→黄色，highlight=True→红色边框。
  > **推荐提示词**: "在 `ui/components/metric_card.py` 中实现 `def metric_card(label, value, sub_text, sub_trend, highlight=False)` 函数。使用 st.markdown 渲染内联 HTML：外层 `<div class='metric-card'>`（highlight=True 加 `.metric-hl` 红色边框），内层 `.metric-label`(11px uppercase 灰白)、`.metric-value`(24px 粗体白)、`.metric-sub`(11px，sub_trend='up'→`.up` 绿色含▲，'down'→`.down` 红色含▼，'warn'→`.warn` 黄色含≈)。CSS class 与 `adcockpit-prototype.html` 中的 `.metric-card`、`.metric-label`、`.metric-value`、`.metric-sub`、`.metric-hl` 完全一致。"

- [ ] **T023** [P] [US1] 实现 StepCard 组件 `ui/components/step_card.py`：可复用函数 `step_card(title, desc, status, time_str, tool_calls=None, on_retry=None)`，status 映射到原型中的 pending/running/done/failed/waiting 样式，tool_calls 为可展开 JSON 详情。
  > **推荐提示词**: "在 `ui/components/step_card.py` 中实现 `def step_card(title, desc, status, time_str, tool_calls=None, on_retry=None)` 函数。使用 st.markdown 渲染内联 HTML：外层 `<div class='step-card status-{status}'>`（done=绿左边框 running=蓝左边框 waiting=黄左边框 failed=红左边框 pending=灰半透明），内层 `.step-icon.{status}`(done=✅ running=🔄span.spin waiting=⏸️ failed=❌ pending=⏳)，`.step-body`(title行+time右对齐+desc描述)，可选 `.tool-call`(默认折叠，点击展开显示JSON pre标签)。tool_calls 为 [{tool_name, request, response}] 列表。CSS class 与原型中的 `.step-card`、`.step-icon`、`.step-body`、`.step-title`、`.tool-call` 完全一致。"

- [ ] **T024** [P] [US1] 实现 ChartWidget 组件 `ui/components/chart_widget.py`：柱状图组件 `chart_widget(title, bars, threshold, max_val)`，bars 为 [{label, value, highlight}] 列表，threshold 处画虚线。
  > **推荐提示词**: "在 `ui/components/chart_widget.py` 中实现 `def chart_widget(title, bars, threshold, max_val)` 函数。使用 st.markdown 渲染 HTML 柱状图：外层 `.chart-card` + `.chart-title`，内层 `.chart-placeholder`(position:relative)，遍历 bars 生成 `.chart-bar`(height=value/max_val*110px, highlight=True 加 `.low` 红色渐变)，柱顶 `.bar-val` 显示数值，柱底 `.bar-label` 显示标签。threshold 处：`<div style='position:absolute;bottom:{threshold/max_val*110+24}px;...;border-top:1px dashed var(--danger)'>` 虚线阈值线。CSS 与原型 `.chart-card`、`.chart-placeholder`、`.chart-bar` 完全一致。"

- [ ] **T025** [P] [US1] 实现 ApprovalCard 组件 `ui/components/approval_card.py`：确认卡片 `approval_card(actions, on_approve, on_reject)`，actions 列表每条显示目标、操作、风险等级颜色标签，底部确认/取消按钮。
  > **推荐提示词**: "在 `ui/components/approval_card.py` 中实现 `def approval_card(actions, on_approve, on_reject)` 函数。使用 st.markdown 渲染 HTML：外层 `.approval-card`(黄色边框 border:1px solid var(--warning))，标题行 `.ac-title`'🛑 待确认 — 调价策略'，遍历 actions 每行 `.ac-row`(左侧目标ID/中间操作描述/右侧风险标签，risk_level='low'→绿色 'medium'→黄色 'high'→红色)，底部 st.columns(2) 渲染 '✅ 确认执行' 按钮 (on_click=on_approve) 和 '✕ 取消' 按钮 (on_click=on_reject)。CSS 与原型 `.approval-card`、`.ac-title`、`.ac-row`、`.btn-confirm`、`.btn-reject` 完全一致。"

- [ ] **T026** [P] [US1] 实现 ReportSummary 组件 `ui/components/report_summary.py`：报告预览 `report_summary(summary_rows, on_copy)`，summary_rows 为 [{label, value}] 列表，底部一键复制按钮。
  > **推荐提示词**: "在 `ui/components/report_summary.py` 中实现 `def report_summary(summary_rows, on_copy)` 函数。使用 st.markdown 渲染 HTML：外层 `.report-summary`，标题行 `.rs-title`'📋 优化报告预览'，遍历 summary_rows 每行 `.rs-row`(label左对齐+value右对齐)，底部 st.button('📋 一键复制报告', on_click=on_copy)，复制后按钮文字变为'✅ 已复制！'2s 后恢复。on_copy 使用 pyperclip.copy() 或 st.write 导出。CSS 与原型 `.report-summary`、`.rs-title`、`.rs-row`、`.copy-btn` 完全一致。"

**Checkpoint**: User Story 1 should be fully functional — 投放优化场景端到端可演示

---

## Phase 4: User Story 2 — 投后素材分析与 AI 内容工厂 (Priority: P2)

**Goal**: 用户输入素材分析指令 → 拉取高/低 CTR 素材 → 多模态帧分析 →
生成口播脚本 → 发布到飞书内容库。

**Independent Test**: 输入"把昨天抖音上CTR最高和最低的3条视频找出来，分析爆款共性，
生成3条新脚本，发布到飞书内容库"，右侧切换为 ContentDashboard 视图。

### Tests for User Story 2

- [ ] **T027** [P] [US2] 创建场景 2 集成测试 `tests/scenarios/test_scenario_2_content.py`：验证内容生产全链路 SSE 事件顺序（supervisor→data_agent→analysis_agent→content_agent→execute_agent→report_agent），验证 analysis_result 包含 creative_insights（前3秒价格锚点/快语速/热门BGM），验证 content 生成 3 条脚本，验证 execute 调用 publish_to_feishu。
  > **推荐提示词**: "在 `tests/scenarios/test_scenario_2_content.py` 中实现内容生产场景端到端测试。测试步骤：(1) POST /execute 发送 '把昨天抖音上CTR最高和最低的3条视频找出来，分析爆款共性，生成3条新脚本，发布到飞书内容库'，(2) 收集 SSE 事件，验证 supervisor 识别 scene='content'，(3) 验证 data_agent 调用 get_top_creatives，(4) 验证 analysis_agent 输出 creative_insights 含前3秒分析，(5) 验证 content_agent 输出 3 条 scripts，(6) 验证 execute_agent 调用 publish_to_feishu，(7) 验证最终 report 包含发布结果。"

### Implementation for User Story 2

- [ ] **T028** [US2] 扩展 Analysis Agent 在 `agents/analysis_agent.py`：新增内容场景分支 — 对素材数据进行 CTR 排名，调用 `analyze_video_frames` Mock 函数获取高点击视频的共性特征（前3秒元素/语速/BGM/价格锚点），输出 `creative_insights`。
  > **推荐提示词**: "在 `agents/analysis_agent.py` 的 `analysis_agent_node` 中新增 content 场景分支。当 current_scene='content' 时：(1) 从 platform_data 中提取 creatives，(2) 按 ctr 降序排列，(3) 对 top 3 creatives 调用 `tools.mock_functions.analyze_video_frames(video_url)` 获取帧分析结果，(4) 汇总共性特征到 analysis_result = {creative_insights: {top_ctr_avg: 0.052, common_features: ['前3秒有价格锚点', '口播语速快(>200字/分)', 'BGM为热门卡点音乐', '视频时长15-30秒', '前3秒出现产品特写'], worst_ctr_avg: 0.018, low_performance_reasons: ['开场无钩子', '语速过慢', 'BGM与内容不匹配']}, analyzed_count: 6}，(5) 更新 task 状态。"

- [ ] **T029** [US2] 实现 Content Agent 在 `agents/content_agent.py`：基于 `creative_insights` 中的共性特征，调用 `generate_script` Mock 函数生成 3 条口播脚本（参数含 template_id='summer_promo' 和特征关键词）。每条脚本约 100-200 字，风格匹配抖音带货口播。
  > **推荐提示词**: "在 `agents/content_agent.py` 中实现 `content_agent_node(state: AgentState) -> dict` 函数。逻辑：(1) 从 analysis_result['creative_insights'] 获取共性特征，(2) 调用 `tools.mock_functions.generate_script(template_id='summer_promo', params={features: common_features, tone: '快节奏带货', length: 'short'})` 3 次生成 3 条口播脚本，(3) 将生成的 scripts 放入 strategy_actions：每条脚本封装为 StrategyAction(target_type='script', action='publish_to_feishu', params={script_content:..., repo:'内容库'}, risk_level='low', requires_approval=False)，(4) 更新 task 状态。生成的脚本应与原型 ContentDashboard 区域展示的格式一致。"

- [ ] **T030** [US2] 扩展 Dashboard 在 `ui/panels/dashboard.py`：实现 ContentDashboard 子视图 — 视频封面网格（含 CTR 标签，前3绿色后3红色）、帧分析结果卡片、AI 生成脚本预览文本区（含'一键改改'编辑按钮）、发布状态标签。
  > **推荐提示词**: "在 `ui/panels/dashboard.py` 的 `render_dashboard()` 中添加 ContentDashboard 分支。当 current_scene='content' 时渲染：(1) 视频封面网格 st.columns(3)×2 行，每格显示 video thumbnail(placeholder) + 名称 + CTR badge(前3绿色/后3红色)，(2) 帧分析结果卡片：st.markdown HTML 渲染 '.step-card' 样式卡片，标题'📊 爆款共性分析'，列表项：前3秒价格锚点/快语速/热门BGM，(3) 脚本预览区：st.columns(1)×3，每列 st.text_area 显示一条脚本内容 + st.button('✏️ 一键改改')，(4) 发布状态标签：st.success('✅ 已发布到飞书内容库') 或 st.warning('⏳ 发布中...')"

---

## Phase 5: User Story 3 — 直播间实时 AI 场控与电商闭环 (Priority: P2)

**Goal**: 用户粘贴直播间数据 → 查询库存 → 自动补货 + 创建优惠券 + 生成催单话术。

**Independent Test**: 粘贴直播间数据，右侧切换为 EcommerceDashboard 视图，
验证并行执行的补货和发券操作。

### Tests for User Story 3

- [ ] **T031** [P] [US3] 创建场景 3 集成测试 `tests/scenarios/test_scenario_3_ecommerce.py`：验证电商场控全链路（supervisor→data_agent→analysis_agent→ecommerce_agent→execute_agent→report_agent），验证 stock=32 标红 → 补货 200 后 232，验证优惠券创建，验证催单话术生成，验证 ERP 日志记录，验证库存变更审批规则。
  > **推荐提示词**: "在 `tests/scenarios/test_scenario_3_ecommerce.py` 中实现电商场控端到端测试。测试步骤：(1) POST /execute 发送 '当前直播间在线2000人，商品A点击率高但转化率下跌。帮我查库存，低于50件自动补200件，创建限时10元优惠券，给主播生成催单话术'，(2) 验证 supervisor 识别 scene='ecommerce'，(3) 验证 data_agent 调用 get_product_stock('A') 返回 stock=32，(4) 验证 ecommerce_agent 生成 actions：update_stock(+200), create_coupon(-10)，(5) 验证 execute_agent 并行执行，(6) 验证 report 包含 GMV 预估。另写测试 `test_stock_approval_rule` 验证库存变更触发审批时 HITL 中断。"

### Implementation for User Story 3

- [ ] **T032** [US3] 实现 Ecommerce Agent 在 `agents/ecommerce_agent.py`：基于直播数据和商品状态，生成电商操作动作列表。包含：库存不足时生成 `update_stock` action（含审批规则判断）、转化率下跌时生成 `create_coupon` action、生成催单话术。所有 action 的风险等级和审批标志按业务规则设定。
  > **推荐提示词**: "在 `agents/ecommerce_agent.py` 中实现 `ecommerce_agent_node(state: AgentState) -> dict` 函数。逻辑：(1) 从 analysis_result 中获取 stock_info 和 live_metrics，(2) 如果 product.stock < 50：生成 action=update_stock(add_amount=200, risk_level='medium', requires_approval=查看用户偏好中的 stock_approval_required)，(3) 如果 current_scene='ecommerce' 且有 conversion_rate 下降：生成 action=create_coupon(discount=10.0, channel='live_comment', total=500, risk_level='low', requires_approval=False)，(4) 调用 `tools.mock_functions.generate_script` 生成催单话术，(5) 将所有 actions 放入 strategy_actions，(6) 附加 log_to_erp('stock_update', {product_id, new_stock, operator})，(7) 更新 task 状态。"

- [ ] **T033** [US3] 扩展 Dashboard 在 `ui/panels/dashboard.py`：实现 EcommerceDashboard 子视图 — 实时在线人数仪表盘、库存状态指示灯（绿/黄/红圆点）、优惠券领取进度条、催单话术展示、预估 GMV 增量卡片。
  > **推荐提示词**: "在 `ui/panels/dashboard.py` 的 `render_dashboard()` 中添加 EcommerceDashboard 分支。当 current_scene='ecommerce' 时渲染：(1) 实时在线人数：st.metric('👥 在线人数', 2000, delta='↑ 5%')，(2) 库存状态灯：st.markdown HTML 渲染大号圆点（stock<50=🔴红色+box-shadow红色辉光, 50-100=🟡黄色, >100=🟢绿色），显示具体库存数字，(3) 优惠券进度条：st.progress(claimed/total) + st.caption(f'已领取 {claimed}/{total}')，(4) 催单话术：st.info box 显示生成的脚本，(5) GMV 预估卡片：st.metric('💰 预估 GMV 增量', '+¥5,000', delta='↑')"

---

## Phase 6: User Story 4 — 跨渠道数据分析与预算决策 (Priority: P2)

**Goal**: 多平台数据聚合 → 按客户分组排名 → 预算再分配建议 → PPT 提纲生成。

**Independent Test**: 输入数据分析指令，右侧切换为 DataDashboard 视图，
验证柱状图和 PPT 提纲。

### Tests for User Story 4

- [ ] **T034** [P] [US4] 创建场景 4 集成测试 `tests/scenarios/test_scenario_4_data_analysis.py`：验证数据分析全链路，验证多平台数据聚合（含部分平台失败时的降级处理），验证客户 ROI 排名输出 Top3/Bottom2，验证预算建议包含具体的转移金额和理由，验证 PPT 提纲生成。
  > **推荐提示词**: "在 `tests/scenarios/test_scenario_4_data_analysis.py` 中实现数据分析端到端测试。测试步骤：(1) POST /execute 发送 '拉取本月所有客户在抖音、腾讯、小红书的消耗、ROI、CPA，按客户汇总，找回报率最高3个和最低2个客户，生成预算建议和PPT提纲'，(2) 验证 supervisor 识别 scene='data_analysis'，(3) 验证 data_agent 调用 get_multi_platform_report（3平台），(4) 验证 analysis_agent 输出 customer_ranking，(5) 验证 strategy_agent 输出 budget_proposal，(6) 验证 report_agent 调用 generate_ppt_outline。另写 `test_partial_platform_failure` 验证一个平台返回错误时系统不中断。"

### Implementation for User Story 4

- [ ] **T035** [US4] 扩展 Supervisor 在 `agents/supervisor.py`：新增数据分析场景的任务拆解逻辑。场景 4 的 task_graph：T1-T3 为并行拉取三个平台报表，T4 为合并分析排名，T5 为预算建议生成，T6 为报告+PPT 提纲生成。
  > **推荐提示词**: "在 `agents/supervisor.py` 的 `supervisor_node` 中新增 data_analysis 场景的 task_graph 生成。当识别到 scene='data_analysis' 时，生成 task_graph：[{id:'T1',type:'fetch_data',platform:'douyin',params:{endpoint:'get_platform_report'}}, {id:'T2',type:'fetch_data',platform:'tencent',params:{endpoint:'get_platform_report'}}, {id:'T3',type:'fetch_data',platform:'xiaohongshu',params:{endpoint:'get_platform_report'}}, {id:'T4',type:'analyze',params:{group_by:'client',metrics:['cost','roi','cpa']},depends_on:['T1','T2','T3']}, {id:'T5',type:'strategize',params:{output:'budget_proposal'},depends_on:['T4']}, {id:'T6',type:'report',params:{output:'ppt_outline'},depends_on:['T5']}]。前 3 个标记为可并行。"

- [ ] **T036** [US4] 扩展 Strategy Agent 在 `agents/strategy_agent.py`：新增数据分析场景 — 基于客户 ROI 排名生成预算再分配建议。Top 3 客户建议追加预算，Bottom 2 客户建议削减，每项建议含金额、比例和理由。
  > **推荐提示词**: "在 `agents/strategy_agent.py` 的 `strategy_agent_node` 中新增 data_analysis 场景分支。当 current_scene='data_analysis' 时：(1) 从 analysis_result 获取 customer_ranking，(2) 对 Bottom 2（ROI最低）生成 budget_reduce actions，对 Top 3 生成 budget_increase actions，(3) 每条 action 包含 target_type='budget', params={change_percent, from_client, to_client, reason}，(4) 填充 analysis_result['budget_proposal'] = {from_client: '客户A', to_client: '客户C', amount: 10000, change_percent: -20, reason: 'ROI仅1.5，远低于客户C的3.2', estimated_roi_improvement: 0.3}，(5) 更新 task 状态。"

- [ ] **T037** [US4] 扩展 Dashboard 在 `ui/panels/dashboard.py`：实现 DataDashboard 子视图 — 按客户分组柱状图（消耗/ROI/CPA 三项对比）、回报率排名 Top3/Bottom2 列表、预算再分配建议表、PPT 提纲可复制文本区。
  > **推荐提示词**: "在 `ui/panels/dashboard.py` 的 `render_dashboard()` 中添加 DataDashboard 分支。当 current_scene='data_analysis' 时渲染：(1) 柱状图：st.markdown HTML 渲染客户 ROI 排名柱状图（5个客户，绿色表示Top3，红色表示Bottom2），(2) Top3 卡片行 st.columns(3)：每卡片显示客户名+ROI+消耗+增长箭头，(3) Bottom2 卡片行 st.columns(2)：每卡片红框显示，(4) 预算分配建议表：st.dataframe 或 markdown table 显示 from_client/to_client/amount/reason，(5) PPT 提纲预览：st.text_area 显示生成的 PPT 提纲结构化文本 + st.button('📋 一键复制')"

---

## Phase 7: User Story 5 — 全链路故障诊断与自主恢复 (Priority: P3)

**Goal**: 输入计划 ID + 现象 → 查询计划状态 → 根因分析 → 自动恢复（出价问题提价 /
审核拒绝替换素材+通知）。

**Independent Test**: 输入故障诊断指令，验证自动根因分析和恢复链路。

### Tests for User Story 5

- [ ] **T038** [P] [US5] 创建场景 5 集成测试 `tests/scenarios/test_scenario_5_diagnosis.py`：验证故障诊断全链路，验证审核拒绝场景自动替换素材+重提审+飞书通知，验证出价过低场景自动提价，验证未知异常场景升级人工处理。
  > **推荐提示词**: "在 `tests/scenarios/test_scenario_5_diagnosis.py` 中实现故障诊断端到端测试。测试 3 个子场景：(1) `test_review_rejected_recovery`：mock get_plan_status 返回 status='rejected', review_status='素材虚假承诺'，验证 execute_agent 调用 replace_creative + resubmit_plan + send_feishu_notification，(2) `test_bid_too_low_recovery`：mock 返回 status='active', bid=5.0，验证 update_bid(+5%)，(3) `test_unknown_error_escalation`：mock 返回无法识别的 status code，验证系统输出诊断失败提示并建议人工介入。"

### Implementation for User Story 5

- [ ] **T039** [US5] 扩展 Analysis Agent 在 `agents/analysis_agent.py`：新增诊断场景分支 — 分析 `plan_status` 数据确定根因类型。支持根因：`review_rejected`（审核拒绝）、`bid_too_low`（出价过低）、`budget_exhausted`（预算耗尽）、`audience_narrow`（定向过窄）、`unknown`（未知）。每种根因附带修复策略建议。
  > **推荐提示词**: "在 `agents/analysis_agent.py` 的 `analysis_agent_node` 中新增 diagnosis 场景分支。当 current_scene='diagnosis' 时：(1) 从 platform_data 获取单个计划的 status/review_status/bid/budget 等字段，(2) 判定根因类型：review_status='rejected'→'review_rejected'，status='active' 但 bid<market_avg→'bid_too_low'，budget<1000→'budget_exhausted'，(3) 输出 analysis_result = {root_cause: 'review_rejected', cause_detail: '素材涉及虚假承诺', suggested_actions: ['replace_creative', 'resubmit_plan', 'notify_user'], severity: 'critical', auto_recoverable: True}，(4) 当 root_cause='unknown' 时，auto_recoverable=False，suggested_actions=['escalate_to_human']，(5) 更新 task 状态。"

- [ ] **T040** [US5] 扩展 Dashboard 在 `ui/panels/dashboard.py`：实现 DiagnosisDashboard 子视图 — 计划状态详情卡片、根因分析结果（标红/标绿）、自动恢复操作日志时间线、飞书通知发送状态。
  > **推荐提示词**: "在 `ui/panels/dashboard.py` 的 `render_dashboard()` 中添加 DiagnosisDashboard 分支。当 current_scene='diagnosis' 时渲染：(1) 计划状态详情卡片：st.markdown HTML 渲染含 id/平台/状态/审核状态/出价/预算的卡片，(2) 根因分析结果：红色/绿色边框卡片，标题'🔴 根因：审核拒绝 — 素材涉及虚假承诺'或'🟢 根因：出价过低 — 已自动提价 5%'，(3) 恢复操作日志：垂直时间线，每步显示时间+操作+结果（参考原型恢复操作日志样式），(4) 飞书通知状态：st.success('✅ 飞书通知已发送给小王') 或 st.warning('⏳ 发送中...')"

---

## Phase 8: Integration & Polish

**Purpose**: 前后端联调、pytest 全量测试、演示就绪

- [ ] **T041** [P] 创建 pytest conftest `tests/conftest.py`：定义共享 fixtures — `mock_llm`（unittest.mock.patch 模拟 LLM 返回结构化 JSON）、`test_client`（httpx.AsyncClient 连接本地 FastAPI app）、`seed_data`（导入并验证 mock_data 与原型一致性）、`sse_collector`（async generator 收集 SSE 事件到 list）。
  > **推荐提示词**: "在 `tests/conftest.py` 中创建 pytest fixtures：(1) `@pytest.fixture(scope='session') def app()`：从 api.main 导入 FastAPI app，(2) `@pytest.fixture async def test_client(app)`：使用 httpx.AsyncClient(app=app, base_url='http://test') 创建测试客户端，(3) `@pytest.fixture(autouse=True) def mock_llm()`：使用 unittest.mock.patch('langchain_openai.ChatOpenAI') 和 patch('langchain_anthropic.ChatAnthropic') 模拟 LLM 调用，返回预定义的结构化 JSON 响应，(4) `@pytest.fixture def seed_data()`：导入 tools.mock_data 中的 DOUYIN_PLANS/TENCENT_PLANS 等，(5) `@pytest.fixture async def sse_collector(test_client, session_id)`：async generator 从 /stream/{sid} 收集所有 SSE 事件到列表并返回。"

- [ ] **T042** [P] 创建 Mock 函数单元测试 `tests/unit/test_mock_functions.py`：验证 24 个 Mock 函数正常返回数据格式正确、业务异常在 ~10% 概率触发、网络异常在 ~5% 概率触发、同一 plan_id 跨函数调用数据一致。
  > **推荐提示词**: "在 `tests/unit/test_mock_functions.py` 中实现：(1) `test_all_functions_return_valid_schema`：遍历 ALL_TOOLS，调用每个函数，验证返回值类型和必要字段存在，(2) `test_data_consistency_with_prototype`：调用 get_top_campaigns('douyin',7,'cost',5)，验证 C001.roi==1.5, C002.roi==2.3, C003.roi==3.1, C004.roi==1.8, C005.roi==2.5（与原型一致），(3) `test_cross_function_consistency`：同一 plan_id 在 get_top_campaigns 和 get_campaign_detail 中返回一致属性，(4) `test_exception_probability`：调用 1000 次函数（用 random.seed(0)），统计异常比例在 8%-12%（业务）和 3%-7%（网络）范围内。"

- [ ] **T043** [P] 创建 AgentState 单元测试 `tests/unit/test_agent_state.py`：验证 AgentState 状态转换正确性，验证 TaskNode status 从 pending→running→done/failed 的合法转换，验证 pending_approval 设值后图执行暂停与恢复。
  > **推荐提示词**: "在 `tests/unit/test_agent_state.py` 中实现：(1) `test_task_node_valid_transitions`：验证 status 只有 pending→running→done|failed 合法，(2) `test_state_initialization`：验证 AgentState 初始化和默认值，(3) `test_strategy_action_requires_approval`：验证 requires_approval=True 时 pending_approval 被正确填充，(4) `test_execution_result_retry_count`：验证失败重试计数。"

- [ ] **T044** 前后端联调验证 `ui/app.py` + `api/main.py`：启动 FastAPI (`uvicorn api.main:app --port 8000`) 和 Streamlit (`streamlit run ui/app.py`)，逐一执行 5 个场景的用户指令。验证 UI 交互与 `adcockpit-prototype.html` 一致：步骤卡片实时更新、指标卡数据正确、柱状图配色一致、审批卡片交互正确、报告可复制。修复所有样式偏差。
  > **推荐提示词**: "联调测试任务。在终端1运行 `uvicorn api.main:app --reload --port 8000`，终端2运行 `streamlit run ui/app.py`。在浏览器中打开 http://localhost:8501，逐一执行以下验证：\n1. 场景1（投放优化）：输入 '检查最近7天在抖音和腾讯广告上，消耗排名Top5的计划里哪些ROI低于2，对不达标的计划自动降价10%'，验证中间面板步骤流（并行Data→Analysis→Strategy→确认卡片→Execute→Report），验证右侧6个指标卡数值与原型一致，验证柱状图C001/T001/C004为红色，验证报告摘要¥5,640/15%/ROI→2.1。点击确认执行。\n2. 场景2（内容生产）：点击内容生产标签，输入素材分析指令，验证ContentDashboard视图。\n3. 场景3（电商场控）：粘贴直播数据，验证EcommerceDashboard视图和库存灯状态变化。\n4. 场景4（数据分析）：输入数据分析指令，验证DataDashboard视图和PPT提纲。\n5. 场景5（故障诊断）：输入诊断指令，验证DiagnosisDashboard视图和根因分析卡片。\n修复任何样式偏差或数据不一致。"

- [ ] **T045** 运行全量测试 `pytest tests/ -v`：确认所有 5 个场景测试 + 单元测试全部通过。
  > **推荐提示词**: "运行 `pytest tests/ -v --tb=short`，确认所有测试通过。如有失败，逐一修复：(1) 检查 mock_llm fixture 是否正确 patch 了 LLM 调用，(2) 检查 SSE 事件顺序是否与预期一致，(3) 检查 mock_data 中的数值是否与原型一致。修复后重新运行直到全部通过。"

**Checkpoint**: All user stories functional, all tests passing, ready for demo

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Setup (T001-T002) — BLOCKS all user stories
- **Phase 3 (US1 - P1)**: Depends on Phase 2 — MVP
- **Phase 4-7 (US2-US5)**: Depends on Phase 2 — Can proceed partially in parallel with US1
- **Phase 8 (Integration)**: Depends on all user story phases

### User Story Dependencies

- **US1 (P1)**: Core path — establishes agents/graph, SSE, all UI components. No dependency on other stories.
- **US2 (P2)**: Depends on US1 for shared infrastructure (graph, SSE, dashboard framework). Adds content-specific branches.
- **US3 (P2)**: Depends on US1. Adds ecommerce-specific branches.
- **US4 (P2)**: Depends on US1. Adds data analysis branches.
- **US5 (P3)**: Depends on US1. Adds diagnosis branches.

### Within Each User Story

- Tests FIRST (if included) → models/agent nodes → endpoints → UI components
- Agent node before its UI dashboard
- Mock data available from Phase 2

### Parallel Opportunities

- T004, T005, T006 can run in parallel (Phase 2)
- T009 (test) can run alongside T010-T026 (implementation) in US1
- T019-T026 (UI components) can all run in parallel (different files)
- T027, T031, T034, T038 (all scenario tests) can run in parallel
- T041, T042, T043 can run in parallel (Phase 8)

---

## Parallel Example: User Story 1

```bash
# Phase 2: Launch Mock data + Mock functions + Tool registry together (T004, T005, T006)
Task: "Create Mock data constants in tools/mock_data.py"
Task: "Implement 24 Mock functions in tools/mock_functions.py"
Task: "Create tool registry in tools/tool_registry.py"

# Phase 3: After Phase 2, launch all UI components together (T019-T026)
Task: "Implement ChatPanel component in ui/panels/chat_panel.py"
Task: "Implement TraceBoard component in ui/panels/trace_board.py"
Task: "Implement InsightDashboard in ui/panels/dashboard.py"
Task: "Implement MetricCard component in ui/components/metric_card.py"
Task: "Implement StepCard component in ui/components/step_card.py"
Task: "Implement ChartWidget in ui/components/chart_widget.py"
Task: "Implement ApprovalCard in ui/components/approval_card.py"
Task: "Implement ReportSummary in ui/components/report_summary.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T008) — **CRITICAL**
3. Complete Phase 3: User Story 1 (T009-T026)
4. **STOP and VALIDATE**: Run `uvicorn api.main:app` + `streamlit run ui/app.py`,
   execute 投放优化 scenario end-to-end
5. Demo if ready — US1 alone demonstrates Multi-Agent + HITL + Three-Column UI

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (投放优化) → Test independently → Demo (MVP!)
3. Add US2 (内容生产) → Test independently → Demo
4. Add US3 (电商场控) → Test independently → Demo
5. Add US4 (数据分析) → Test independently → Demo
6. Add US5 (故障诊断) → Test independently → Demo
7. Phase 8: Full integration test suite → Final demo

### Task Stats

| Phase | Tasks | Story |
|-------|-------|-------|
| Setup | T001-T002 | — |
| Foundational | T003-T008 | — |
| US1 (P1) | T009-T026 | 投放优化 |
| US2 (P2) | T027-T030 | 内容生产 |
| US3 (P2) | T031-T033 | 电商场控 |
| US4 (P2) | T034-T037 | 数据分析 |
| US5 (P3) | T038-T040 | 故障诊断 |
| Integration | T041-T045 | 联调+全量测试 |
| **Total** | **45 tasks** | 5 stories |

---

## Notes

- [P] tasks = different files, no dependencies → can be implemented in parallel by
  different AI Coding sessions
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Mock data in `tools/mock_data.py` is the single source of truth — all UI values
  and test assertions reference it
- All CSS class names and values must match `adcockpit-prototype.html` exactly
- After each task, verify the file runs without syntax errors before proceeding
- Commit after each logical group of tasks
