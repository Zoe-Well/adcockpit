# Data Model: AdCockpit v1.0

**Updated**: 2026-06-11

## Core Entities (Implemented)

### Campaign（投放计划）

Stored in `tools/mock_data.py` as `DOUYIN_PLANS` and `TENCENT_PLANS` (mutable lists).

| Field | Type | Example |
|-------|------|---------|
| `id` | `str` | `"C001"` |
| `name` | `str` | `"夏季促销-A"` |
| `_platform` | `str` | `"douyin"` (added at runtime) |
| `cost` | `float` | `15200` |
| `roi` | `float` | `1.5` |
| `cpa` | `float` | `40.0` |
| `ctr` | `float` | `0.035` |
| `cvr` | `float` | `0.038` |
| `bid` | `float` | `25.0` |
| `budget` | `float` | `5000` |
| `status` | `str` | `"active"` |

### OptimParams（优化参数）

Stored in `st.session_state.optim_params`:

| Field | Default |
|-------|---------|
| `platforms` | `["douyin","tencent"]` |
| `days` | `7` |
| `top_n` | `5` |
| `roi_threshold` | `2.0` |
| `bid_adjust_pct` | `-10` |
| `budget_adjust_pct` | `-20` |
| `risk_confirm` | `"medium"` |

### ContentParams（内容生产参数）

Stored in `st.session_state.content_params`:

| Field | Default |
|-------|---------|
| `platform` | `"douyin"` |
| `date` | `"yesterday"` |
| `top_n` | `3` |
| `worst_n` | `3` |
| `template_id` | `"summer_promo"` |
| `auto_publish` | `True` |

### PendingCreate（待确认创建）

Stored in `st.session_state._pending_create`:

| Field |
|-------|
| `platform`, `name`, `budget`, `bid`, `targeting` |

### AgentState（LangGraph 状态）

Defined in `agents/state.py` — used by FastAPI/LangGraph mode:

```python
class AgentState(TypedDict):
    user_input: str
    task_graph: List[TaskNode]
    platform_data: List[PlatformData]
    analysis_result: Dict
    strategy_actions: List[StrategyAction]
    execution_results: List[ExecutionResult]
    report: Dict
    pending_approval: Optional[List[StrategyAction]]
    conversation_history: List[Dict]
    error_log: List[Dict]
    session_id: str
    current_scene: Literal["ad_placement","content","ecommerce","data_analysis","diagnosis"]
```
