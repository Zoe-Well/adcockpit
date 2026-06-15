1. 文档驱动，且可接受外部文档知识驱动
2. clarify很有用
3. 生成一份基于用户场景描述的项目实现状态，开发过程实时更新项目实现状态；

---

## 开发避坑指南（反复出现的 Bug 模式）

### Trace Board 场景映射
新增业务场景时三个地方必须同步：
- `TRACE` 配置加新场景的 flow + steps
- `runXxx()` 第一行调 `setBizScene('xxx')`
- 审批卡片 + 参数卡片 加该场景专属分支

### 审批后才执行
- `runXxx()` 只做动画，不调 API
- `confirmXxx()` 只调 API，`setTraceStep` 放成功回调内

### 参数自定义
- 数字参数 state 用字符串类型（如 `useState('5000')`），直接用 `e.target.value` 赋值，不做 Number 转换
- 提交 API 时才 `parseInt()` / `parseFloat()` 转换
- 如果改成 `Number(e.target.value)||default`，用户清空输入时会回退到默认值，无法自由输入

### 数据持久化
- 从 `DOUYIN_PLANS` 原对象保存 JSON，不用 `get_top_campaigns` 的副本

### 场景专属 Dashboard
新增业务场景时必须添加专属仪表盘视图，不能回退到默认 optimize 视图：
- 在 `tab === 'xxx'` 处增加条件分支
- 展示与该场景业务相关的指标卡+图表+记录表
- US2 内容生产：脚本数/飞书文档/模板/爆款特征/生成记录
- US6 广告投放：在投计划/本次创建/总预算/平台分布/创建记录

### 变量提升
- `const` 不提升，定义顺序要正确（先基础后依赖）
    每次测试问题时也可以参考已经实现的功能去描述我们想要的效果，AI更好理解
    每次测试时就可以具体的去定位未实现或者出问题的场景。
