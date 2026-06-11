# 飞书文档 API 接入教程

> 让 AdCockpit 自动创建飞书文档 —— 从零开始，一步一步来。

---

## 一、创建飞书应用（5分钟）

### Step 1：进入飞书开放平台

打开 https://open.feishu.cn ，用你的飞书账号登录。

### Step 2：创建企业自建应用

1. 点击左侧「开发者后台」→「创建应用」
2. 选择「**企业自建应用**」
3. 应用名称填 `AdCockpit`，描述随意
4. 点击「创建」

### Step 3：获取凭证

1. 在应用页面左侧点击「**凭证与基础信息**」
2. 你会看到：
   - **App ID**：`cli_xxxxxxxxxxxx`
   - **App Secret**：`xxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 二、配置权限（2分钟）

### Step 4：添加 API 权限

在应用页面左侧点击「**权限管理**」，搜索并开通以下权限：

| 搜索关键词 | 权限名称 | 用途 |
|-----------|---------|------|
| `docx:document` | 创建文档 | 新建飞书文档 |
| `docx:document:create` | 写入文档内容 | 往文档里写内容 |
| `drive:permission` | 管理文档权限 | 让文档出现在你的主页 |

> ⚠️ 每添加一个权限后，点击「批量开通」确认。

### Step 5：发布应用

1. 左侧点击「**版本管理与发布**」
2. 点击右上角「**创建版本**」，填写版本号（如 `1.0.0`）
3. 点击「**申请发布**」
4. 如果提示需要管理员审批，联系你的飞书管理员通过一下

> 💡 如果是你自己创建的测试企业，你会同时是管理员，直接在飞书客户端里审批即可。

---

## 三、配置项目（1分钟）

### Step 6：填入凭证

编辑项目根目录的 `.env.example` 文件（或新建 `.env` 文件），写入：

```bash
FEISHU_APP_ID=cli_你的AppID
FEISHU_APP_SECRET=你的AppSecret

# 可选：指定文件夹，让文档出现在你的飞书云文档里
# 获取方式见下方
FEISHU_FOLDER_TOKEN=
```

### Step 7（可选）：设置文件夹

如果想创建的文档**自动出现在你的飞书云文档主页**：

1. 打开飞书桌面端或网页端 → 云文档
2. 新建一个文件夹，比如叫「AdCockpit 脚本」
3. 进入该文件夹，看浏览器地址栏：
   ```
   https://xxx.feishu.cn/drive/folder/fldcnXXXXXXXXXXXX
   ```
4. 复制 `fldcnXXXXXXXXXXXX` 这段
5. 填入第 6 行：`FEISHU_FOLDER_TOKEN=fldcnXXXXXXXXXXXX`

---

## 四、测试连接

### Step 8：运行测试

在项目根目录执行：

```bash
py -c "
from tools.feishu_client import create_document
r = create_document('测试文档', '如果你看到这个，说明飞书连接成功了！')
print('文档链接:', r['url'])
print('Mock模式:', r.get('mock', False))
"
```

如果输出 `Mock模式: False` 且有一个 `https://bytedance.feishu.cn/docx/...` 链接，说明🚀 连接成功！

---

## 五、AdCockpit 中的使用

### 代码位置

| 文件 | 作用 |
|------|------|
| `tools/feishu_client.py` | 飞书 API 客户端：创建文档、获取Token、权限共享 |
| `.env.example` | 凭证配置（你的 App ID / Secret） |
| `ui/panels/chat_panel.py` | 内容生产按钮 → 点击即调用飞书创建文档 |
| `ui/panels/trace_board.py` | 投放优化确认 → 自动生成飞书优化报告 |

### 工作流程

```
你点击 "🚀 开始生产"
       ↓
  generate_script() 生成脚本内容
       ↓
  publish_scripts() → feishu_client.create_document()
       ↓
  飞书 API → 创建文档 → 写入内容 → 设置权限
       ↓
  返回文档链接，显示在聊天面板
```

### 自动发布的场景

| 场景 | 触发 | 创建内容 |
|------|------|---------|
| 🎬 内容生产 | 点击「🚀 开始生产」 | N 条带货脚本（各一个飞书文档） |
| 🎯 投放优化 | 确认执行调价 | 1 份优化报告 |

### 凭证优先级

1. 先读项目根目录的 `.env` 文件
2. 如果没有，读 `.env.example` 作为 fallback
3. 两个都没有 → 自动降级为 Mock 模式（不影响 Demo 演示）

---

## 常见问题

**Q: 提示"App ID 或 Secret 无效"？**
A: 检查 `.env.example` 里的值是否和飞书开放平台「凭证与基础信息」页面一致。

**Q: 文档创建成功但主页看不到？**
A: 设置 `FEISHU_FOLDER_TOKEN` 指定目标文件夹，或者通过返回的链接直接访问。

**Q: 提示"无权限"？**
A: 回到飞书开放平台 → 权限管理，确认 `docx:document` 和 `drive:permission` 已开通并已发布新版本。
