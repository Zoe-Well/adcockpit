# API Contracts: AdCockpit

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-09

## REST Endpoints

### POST /execute

触发 Agent 图执行。

**Request**:
```json
{
  "user_input": "检查最近7天在抖音和腾讯广告上...",
  "session_id": "demo-2026-0609"
}
```

**Response** (200):
```json
{
  "session_id": "demo-2026-0609",
  "status": "running",
  "current_scene": "ad_placement",
  "task_graph": [
    {"id":"T1","type":"fetch_data","platform":"douyin","status":"pending"},
    {"id":"T2","type":"fetch_data","platform":"tencent","status":"pending"}
  ]
}
```

### POST /approve/{session_id}

发送审批确认信号，恢复 LangGraph 图执行。

**Request**: (empty body)
**Response** (200):
```json
{
  "session_id": "demo-2026-0609",
  "status": "resumed",
  "approved_actions": ["C001_update_bid", "T001_update_bid", "T001_update_budget", "C004_update_bid"]
}
```

### POST /reject/{session_id}

发送审批拒绝信号，跳过待审批操作。

**Request**: (empty body)
**Response** (200):
```json
{
  "session_id": "demo-2026-0609",
  "status": "cancelled",
  "rejected_actions": ["C001_update_bid", "T001_update_bid", "T001_update_budget", "C004_update_bid"]
}
```

### GET /session/{session_id}/state

查询当前会话的 AgentState。

**Response** (200):
```json
{
  "session_id": "demo-2026-0609",
  "current_scene": "ad_placement",
  "execution_results": [...],
  "pending_approval": null,
  "report": {...}
}
```

## SSE Event Stream

### GET /stream/{session_id}

Server-Sent Events 端点，推送 Agent 执行过程中的状态变化。

**Event types**:

```
event: step_start
data: {"node":"supervisor","ts":"2026-06-09T10:00:00Z"}

event: step_update
data: {"node":"data_agent","status":"running","tool":"get_top_campaigns","platform":"douyin","ts":"2026-06-09T10:00:01Z"}

event: step_complete
data: {"node":"data_agent","status":"done","tool":"get_top_campaigns","platform":"douyin","duration_ms":2100,"result":{"count":5},"ts":"2026-06-09T10:00:03Z"}

event: approval_required
data: {"actions":[{"target":"C001","action":"update_bid","params":{"new_bid":22.5},"risk":"medium"}],"ts":"2026-06-09T10:00:08Z"}

event: step_error
data: {"node":"data_agent","status":"failed","tool":"get_top_campaigns","platform":"kuaishou","error":"Timeout","retry_count":1,"ts":"2026-06-09T10:00:04Z"}

event: execution_complete
data: {"session_id":"demo-2026-0609","total_duration_ms":8500,"report":{...}}
```

### SSE → Streamlit Mapping

| SSE Event | Streamlit Component Updated |
|-----------|---------------------------|
| `step_start` | TraceBoard: new step card with `status=running` spinner |
| `step_update` | TraceBoard: update existing card status icon |
| `step_complete` | TraceBoard: card → `status=done` ✅; Dashboard: refresh metrics |
| `approval_required` | ChatPanel: render ApprovalCard; TraceBoard: step → ⏸️ |
| `step_error` | TraceBoard: card → `status=failed` ❌ + retry button |
| `execution_complete` | ChatPanel: final message; Dashboard: show report summary |
