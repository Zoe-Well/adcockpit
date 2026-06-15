# Tasks: AdCockpit v2 — FastAPI + Jinja2 前后端分离迁移

**Goal**: 用 FastAPI + Jinja2 模板完全替换 Streamlit 前端，实现与 `adcockpit-v2-prototype.html` 像素级一致的界面，同时保留所有现有业务功能。

**Architecture**: `FastAPI` + `Jinja2 Templates` + `Vanilla JS` → `Mock Functions` + `Feishu Client`

---

## Phase 1: 项目骨架 (Setup)

### T001
创建 `v2/` 目录结构：
- `v2/main.py` — FastAPI 入口
- `v2/routes.py` — 路由定义
- `v2/templates/` — Jinja2 模板
- `v2/static/` — CSS/JS 静态文件
- `v2/api/` — REST API 端点

> **提示词**: 在项目根目录创建 `v2/` 目录及子目录 `v2/templates/`, `v2/static/css/`, `v2/static/js/`, `v2/api/`。所有文件暂为空 `__init__.py`。

### T002
创建 FastAPI 主入口 `v2/main.py`：挂载静态文件目录，注册路由，配置 Jinja2 模板引擎，CORS 全开。

> **提示词**: 在 `v2/main.py` 中创建 FastAPI 应用。挂载 `v2/static` 为 `/static`。使用 `Jinja2Templates` 指向 `v2/templates/`。include `v2/routes.py` 的路由。CORS 允许所有来源。添加 startup 事件初始化 SSEManager。参考 `api/main.py` 的模式。

### T003
拆分原型 HTML 为 Jinja2 模板 `v2/templates/base.html`（骨架：sidebar + header + 三栏布局），`v2/templates/index.html`（继承 base，填充默认内容）。

> **提示词**: 将 `adcockpit-v2-prototype.html` 拆分为两个 Jinja2 模板。`base.html` 包含：`<head>` 内联 CSS、sidebar 结构、header 结构、三栏布局的容器 div、底部 JS 脚本引用。`index.html` 继承 base，填充 Chat Panel、Trace Board、Dashboard 的 HTML 内容。所有中文标签和内容放 index 中。CSS 变量和全局样式放 `<style>` 标签中（不要外部文件，保持独立）。

---

## Phase 2: 后端 API 层 (Core)

### T004
创建 `v2/api/campaigns.py` — 投放计划 REST API：
- `GET /api/campaigns?platform=douyin&days=7&top_n=5`
- `POST /api/campaigns/optimize` 执行优化并返回结果
- `POST /api/campaigns/create` 创建新计划

> **提示词**: 在 `v2/api/campaigns.py` 中创建 FastAPI APIRouter。  
> 1. `GET /api/campaigns` — 调用 `tools.mock_functions.get_top_campaigns` 返回 JSON。query params: platform, days, metric, top_n。返回值包含 `{plans: [...], total_cost, avg_roi, below_threshold}`。  
> 2. `POST /api/campaigns/optimize` — 接收 `{platforms, days, top_n, roi_threshold, bid_adjust_pct, budget_adjust_pct}`。调用 `get_top_campaigns` + `update_bid` + `update_budget`，返回 `{changes: [...], below_count, total_plans}`。  
> 3. `POST /api/campaigns/create` — 接收 campaign 参数，调用 `create_campaign`，返回新计划 JSON。

### T005
创建 `v2/api/content.py` — 内容生产 REST API：
- `POST /api/content/generate` 生成脚本（不发布）
- `POST /api/content/publish` 发布到飞书

> **提示词**: 在 `v2/api/content.py` 中创建 APIRouter。  
> 1. `POST /api/content/generate` — 接收 `{platform, top_n, template_id}`，调用 `generate_script` 生成 N 条脚本，返回 `{scripts: [...]}`。不调用飞书。  
> 2. `POST /api/content/publish` — 接收 `{scripts, platform, template_id}`，调用 `publish_scripts`，返回 `{urls: [...]}`。

### T006
创建 `v2/api/intent.py` — 意图识别 API：
- `POST /api/intent/classify` 返回场景分类

> **提示词**: 在 `v2/api/intent.py` 中创建 APIRouter。`POST /api/intent/classify` 接收 `{user_input}`，调用 `agents/supervisor.py` 的 `_is_conversational_intent` 和 `_detect_biz_scene`（或等效逻辑），返回 `{type: "conversational"|"business", scene: "ad_placement"|"content"|..., reply: "..."}`。

### T007
创建 `v2/routes.py` — 聚合所有 router，定义页面路由：
- `GET /` 返回 index 页面
- include 所有 API router

> **提示词**: 在 `v2/routes.py` 中创建主路由文件。`GET /` 返回 `templates.TemplateResponse("index.html", {"request": request})`。include `v2/api/campaigns.py`, `v2/api/content.py`, `v2/api/intent.py` 的 router。

---

## Phase 3: 前端 JS 交互层

### T008
创建 `v2/static/js/app.js` — 核心 JS 逻辑：
- 侧边栏导航切换（切换 active 状态 + 更新右侧 dashboard）
- Chat 发送消息 → 调用意图识别 API → 展示参数卡片或对话回复
- 参数卡片提交 → 调用优化/内容 API → 更新 Trace Board + Dashboard

> **提示词**: 创建 `v2/static/js/app.js`。使用 Vanilla JS（无框架）。  
> 1. 侧边栏：给每个 `.sidebar-item` 绑定 click 事件，切换 `.active` class，调用对应的数据加载函数。  
> 2. Chat：点击发送或回车时，POST `/api/intent/classify` 判断意图。如果是 `conversational`，直接在 chat-msgs 追加对话气泡。如果是 `business`，渲染参数卡片 HTML。  
> 3. 参数卡片：优化参数提交 → POST `/api/campaigns/optimize` → 成功后调用 `animateTrace()` 流式点亮 Trace Board → 更新 dashboard 数据。  
> 4. 渲染函数：`renderMetrics(data)`, `renderChart(data)`, `renderTable(data)`, `renderAlerts(data)`, `renderTraceSteps(scene)`.

### T009
创建 `v2/static/js/trace.js` — Trace Board 动画引擎：
- `animateTrace(scene, callback)` 逐帧点亮流程图 + 文字打字效果
- 每帧更新对应 `.flow-dot` 和 `.step-card` 的状态

> **提示词**: 创建 `v2/static/js/trace.js`。  
> `animateTrace(scene, callback)`：定义每种 scene 的节点列表。使用 `setInterval` 每 150ms 执行一帧：将当前节点设为 `.active`，上一节点设为 `.done`，更新步骤卡片文字（逐字显示）。所有节点完成后调用 callback。  
> 支持 scene: `optimize`, `create`, `content`。  
> 工具函数：`typeText(element, text, speed)` 模拟打字效果。

### T010
创建 `v2/static/js/dashboard.js` — 仪表盘数据渲染：
- `loadDashboard(tab)` 根据当前 tab 调用 API 并渲染对应内容
- 表格分页和排序（客户端实现）

> **提示词**: 创建 `v2/static/js/dashboard.js`。  
> `loadDashboard(tab)`：根据 tab 值调用不同 API 渲染 dashboard。  
> - optimize: 调用 `/api/campaigns` → 渲染指标卡、ROI 柱状图、表格、告警、报告。  
> - create: 渲染创建表单和已创建计划列表。  
> - content: 调用 `/api/content/generate` 预览脚本。  
> 表格分页：每页 5 条，`prevPage()` / `nextPage()` 控制。排序：点击表头切换 sort key 和 direction。

---

## Phase 4: 模板完善

### T011
完善 `v2/templates/index.html` — 确保所有 Jinja2 变量和循环正确，初始状态与原型一致（侧边栏、三栏布局、默认数据）。

### T012
在模板中添加 JS 引用：`<script src="/static/js/trace.js"></script>`, `<script src="/static/js/dashboard.js"></script>`, `<script src="/static/js/app.js"></script>`。

---

## Phase 5: 测试与验证

### T013
启动应用：`uvicorn v2.main:app --port 8000 --reload`。浏览器打开 `http://localhost:8000`。

验证清单：
- [ ] 侧边栏 6 个按钮正常切换，高亮正确
- [ ] 对话面板发送消息 → 意图识别 → 正确响应
- [ ] 优化参数卡片 → 提交 → 数据正确更新
- [ ] Trace Board 流式动画逐帧点亮
- [ ] 仪表盘指标卡/图表/表格数据正确
- [ ] 投放计划创建流程完整
- [ ] 内容生产预览 → 确认 → 飞书发布
- [ ] 界面与 `adcockpit-v2-prototype.html` 一致

### T014
修复所有视觉差异 — 调整 CSS 直到与原型一致。

---

## 依赖关系

```
Phase 1 (T001-T003) → Phase 2 (T004-T007) → Phase 3 (T008-T010) → Phase 4 (T011-T012) → Phase 5 (T013-T014)
```

Phase 2 和 Phase 3 可以部分并行（API 和 JS 是独立的）。

## 文件清单（预计）

| 文件 | 用途 |
|------|------|
| `v2/main.py` | FastAPI 入口 |
| `v2/routes.py` | 页面路由 + API 聚合 |
| `v2/api/campaigns.py` | 投放计划 API |
| `v2/api/content.py` | 内容生产 API |
| `v2/api/intent.py` | 意图识别 API |
| `v2/templates/base.html` | Jinja2 骨架模板 |
| `v2/templates/index.html` | 主页面 |
| `v2/static/js/app.js` | 核心交互逻辑 |
| `v2/static/js/trace.js` | Trace Board 动画 |
| `v2/static/js/dashboard.js` | Dashboard 渲染 |

## 启动命令

```bash
uvicorn v2.main:app --port 8000 --reload
# 打开 http://localhost:8000
```
