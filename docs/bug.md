# AdCockpit Bug 记录

## [2026-06-17] 意图识别 scene→tab 映射缺失（ad_placement≠optimize）

**现象**: 用户输入"优化投放"，意图识别返回 `ad_placement`，但前端不跳转到投放优化标签页。

**根因**: 后端 scene 名 (`ad_placement`) 和前端 Tab 名 (`optimize`) 不一致。`sendMsg()` 只对 `create` 和 `content` 做了 `setTab()`，`ad_placement` / `ecommerce` / `data_analysis` / `diagnosis` 全部漏掉。

**修复**: 在 `sendMsg()` 中添加 `sceneToTab` 映射表覆盖全部 6 个场景，统一 `setTab()` + 清空 `agentSteps`。

---

## [2026-06-17] content 场景未跳转到内容生产标签页

**现象**: LLM 识别为内容生产场景后，`sendMsg()` 只设了 `showParam=true`，没有调用 `setTab('content')`。

**根因**: `sendMsg()` 的 if-else 链只覆盖了 `create`（`setTab('create')`），`content` 走到通用 else 分支。

**修复**: 添加 `else if(d.scene==='content'){setTab('content')}` 分支。

---

## [2026-06-17] 确认执行后 report 节点提前点亮（三个场景通用）

**现象**: US1/US2/US6 点击"确认执行"后，report 节点立即显示绿色 done ✓，但实际 API 调用尚未完成。

**根因**: `confirmOptimize()` / `confirmContent()` / `confirmCreate()` 都在 `await fetch()` 之前就 `setAgentSteps(report: done)`。

**修复**: 改为两步 `setAgentSteps`：
1. 确认点击 → execute `running`（◉转圈）+ report `running`（◉转圈）
2. API 返回 → execute `done`（✓）+ report `done`（✓）富文本
3. API 失败 → execute `done`（部分完成）+ report `failed`（✕）

---

## [2026-06-17] "广告投放"被识别为 ad_placement 而非 create

**现象**: 用户输入"广告投放"，模型识别为 `ad_placement`（投放优化），实际应该是 `create`（新建投放计划）。

**根因**: 
1. LLM System Prompt 中 `ad_placement` 和 `create` 的描述都含"投放"，模型无法区分
2. Keyword fallback 把"投放"归入优化类引导回复

**修复**: 
1. System Prompt 重写：明确"投放"单独出现 = create，"投放优化" = ad_placement
2. Keyword fallback 重构：精确关键词路由，"投放"/"新建"/"创建" → create，"优化"/"调价"/"ROI" → ad_placement

---

## [2026-06-16] DeepSeek API 偶发 Connection Error

**现象**: `[LLM FAIL] input='你是谁' error=Connection error.`

**根因**: 网络波动导致 DeepSeek API 调用偶发超时/断连。`intent.py` 中只尝试一次即回退到关键词匹配，导致用户看到生硬的回复。

**修复**: 在 `intent.py` 的 `classify()` 函数中增加 `for attempt in range(3)` 重试机制，每次失败等待 1 秒。3 次全失败才回退关键词匹配。

---

## [2026-06-16] 审批卡片数据写死

**现象**: 投放优化审批卡片始终显示 C001/T001/C004 的固定数据，与实际不达标计划不一致。

**根因**: 审批卡片在 API 调用前显示，`runOptimize()` 中动画和审批是同步的，但数据源是硬编码数组。

**修复**: `runOptimize()` 中添加 `fetch(/api/campaigns/all)` 预加载实际不达标计划数据存入 `approvalData` state，审批卡片从 state 动态渲染。

---

## [2026-06-16] 三元表达式缺少 else 分支

**现象**: `vite:oxc` 编译报错 `Expected ':' but found '}'`。

**根因**: JSX 中 `{condition ? <Component/>}` 写法 TypeScript 允许但 Vite OXC 解析器不允许，必须写成 `{condition ? <Component/> : null}`。

**修复**: 所有三元表达式添加 `: null` 或 `: <fallback/>` 分支。

---

## [2026-06-15] `_find_plan` 返回副本导致 update_bid 无效

**现象**: 调用 `update_bid` 后数据未持久化，Dashboard 显示旧值。

**根因**: `_find_plan()` 使用 `return dict(p)` 返回计划副本，`update_bid` 修改副本而原数据不变。

**修复**: 改为 `return p` 返回原始引用；`update_bid` 显式写 `plan["bid"] = new_bid`。

---

## [2026-06-15] LLM 未接入（DeepSeek API Key 路径错误）

**现象**: `[LLM FAIL] Authentication Fails, Your api key: ***`

**根因**: `config.py` 中 `load_dotenv()` 无参数，默认从 CWD 查找 `.env`。uvicorn 进程 CWD 不是项目根，找不到 `backend/.env`。

**修复**: 改为 `load_dotenv(Path(__file__).parent.parent.parent / ".env")` 使用绝对路径。

---

## [2026-06-15] Agent 端点 KeyError: 'task_graph'

**现象**: `POST /api/agent/optimize` 返回 500，报 `KeyError: 'task_graph'`。

**根因**: `backend/app/agents/analysis_agent.py` 是旧版副本，要求完整的 `AgentState` TypedDict（含 task_graph）。Agent 端点创建的简化 dict 不含此字段。

**修复**: 重写 agent 文件，接受 plain dict，不依赖 task_graph。

---

## [2026-06-16] Trace Board 场景错乱

**现象**: 广告投放/内容生产的 Trace Board 显示投放优化的步骤。

**根因**: `runCreate()` / `runContent()` 未调用 `setBizScene('xxx')`，`traceScene` 回退到 `optimize`。

**修复**: 所有 `run*()` 函数第一行加 `setBizScene('场景名')`。此规则已记入 `tips.md`。
