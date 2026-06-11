# Data Model: AdCockpit

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-09

## Core Entities

### 1. Campaign (广告计划)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `str` | 计划唯一标识 | `"C001"` |
| `platform` | `Literal["douyin","tencent","kuaishou","xiaohongshu"]` | 所属平台 | `"douyin"` |
| `name` | `str` | 计划名称 | `"夏季促销-A"` |
| `cost` | `float` | 累计消耗 (元) | `15200.0` |
| `roi` | `float` | 投入产出比 | `1.5` |
| `cpa` | `float` | 单次转化成本 (元) | `40.0` |
| `ctr` | `float` | 点击率 | `0.038` |
| `cvr` | `float` | 转化率 | `0.042` |
| `bid` | `float` | 当前出价 (元) | `25.0` |
| `budget` | `float` | 日预算 (元) | `5000.0` |
| `status` | `Literal["active","paused","pending_review","rejected"]` | 计划状态 | `"active"` |
| `review_status` | `Optional[str]` | 审核状态 | `"approved"` |
| `creative_ids` | `List[str]` | 关联素材 ID 列表 | `["V001","V002"]` |

### 2. Creative (创意素材)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `str` | 素材唯一标识 | `"V001"` |
| `platform` | `str` | 所属平台 | `"douyin"` |
| `name` | `str` | 素材名称 | `"夏季促销口播-A"` |
| `type` | `Literal["video","image","text"]` | 素材类型 | `"video"` |
| `url` | `str` | 素材地址 (Mock) | `"https://mock.cdn/videos/v001.mp4"` |
| `ctr` | `float` | 点击率 | `0.05` |
| `completion_rate` | `float` | 完播率 | `0.8` |
| `created_at` | `str` | 创建日期 (ISO) | `"2026-06-08"` |

### 3. Product (电商商品)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `str` | 商品 ID | `"A"` |
| `name` | `str` | 商品名称 | `"爆款T恤"` |
| `stock` | `int` | 当前库存 | `32` |
| `reserved` | `int` | 预留库存 | `10` |
| `price` | `float` | 售价 (元) | `99.0` |
| `status` | `Literal["on_sale","off_shelf","low_stock"]` | 商品状态 | `"low_stock"` |

### 4. Coupon (优惠券)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `coupon_id` | `str` | 优惠券 ID | `"CP001"` |
| `product_id` | `str` | 关联商品 ID | `"A"` |
| `discount` | `float` | 优惠金额 (元) | `10.0` |
| `channel` | `Literal["live_comment","feed","direct"]` | 发放渠道 | `"live_comment"` |
| `claimed` | `int` | 已领取数 | `0` |
| `total` | `int` | 总数量 | `500` |

### 5. LiveMetrics (直播间指标)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `room_id` | `str` | 直播间 ID | `"ROOM-001"` |
| `online` | `int` | 在线人数 | `2000` |
| `gmv` | `float` | 累计 GMV (元) | `85000.0` |
| `conversion_rate` | `float` | 转化率 | `0.03` |

### 6. AgentState (LangGraph 运行时状态)

Full definition in [spec.md](../spec.md#functional-requirements--langgraph-state-定义).
Key sub-entities:

- **TaskNode**: `id, type, platform?, params, depends_on, status`
- **PlatformData**: `platform, endpoint, data[], fetched_at, error?`
- **StrategyAction**: `target_id, target_type, action, params, risk_level, expected_effect, requires_approval`
- **ExecutionResult**: `action, status, response?, error?, retry_count, executed_at`

### 7. Report (报告)

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | 报告标题 |
| `scene` | `str` | 场景类型 |
| `summary` | `List[str]` | 摘要要点 |
| `actions_taken` | `List[ExecutionResult]` | 已执行操作 |
| `recommendations` | `List[str]` | 后续建议 |
| `ppt_outline` | `Optional[List[Dict]]` | PPT 提纲 (场景 4) |
| `generated_at` | `str` | 生成时间 (ISO) |

## Entity Relationships

```
Campaign 1──* Creative       (一个计划可关联多个素材)
Product  1──* Coupon         (一个商品可有多个优惠券)
Product  1──1 LiveMetrics    (一个商品关联一组直播间指标)
AgentState 1──* TaskNode     (状态包含任务图)
AgentState 1──* PlatformData (状态包含多平台数据)
AgentState 1──* StrategyAction
AgentState 1──* ExecutionResult
AgentState 1──1 Report
```

## State Transitions

### TaskNode Status
```
pending → running → done
                  → failed → retrying → running → done
                  → failed → (max retries) → failed (terminal)
                  → awaiting_approval → done (approved)
                                      → cancelled (rejected)
```

### Campaign Status
```
active → paused (manual)
active → pending_review (after creative change)
pending_review → active (approved)
pending_review → rejected (审核拒绝)
```
