# AdCockpit 部署实践教程：GitHub + Vercel + Railway + 阿里云域名

> 从零到上线，每一步都踩过坑，每一个坑都写了解决方案。  
> 以域 `zoewell.cn` 为例，你的域换成自己的即可。

**预估耗时**：首次约 1 小时  
**费用**：Railway $5/月（免费额度）、Vercel 免费、阿里云域 ¥60/年

---

## 一、整体架构

```
用户浏览器（国内）
    │
    ▼
zoewell.cn 的 DNS 记录
    ├── adcockpit.zoewell.cn  ──CNAME──→  cname.vercel-dns.com  ──→  Vercel 前端
    └── api.zoewell.cn       ──CNAME──→  xxx.up.railway.app    ──→  Railway 后端
```

**核心概念**（搞懂这一步，后面都是填表）：

| 概念 | 谁给的 | 干什么 |
|------|--------|--------|
| `adcockpit.vercel.app` | Vercel 自动给 | 前端实际地址，国内打不开 |
| `xxx.up.railway.app` | Railway 自动给 | 后端实际地址，国内慢 |
| `adcockpit.zoewell.cn` | 你买 + 你配 | 前端的"门面"，发给面试官 |
| `api.zoewell.cn` | 你买 + 你配 | 后端的"门面"，前端代码里默默用 |
| DNS 记录 | 你在阿里云填 | 告诉互联网"这个域去哪" |

---

## 二、前置准备

| 需要 | 去哪弄 | 做什么 |
|------|--------|--------|
| GitHub 账号 | [github.com](https://github.com) | 代码仓库，推代码即部署 |
| Railway 账号 | [railway.app](https://railway.app) | 托管 Python 后端 |
| Vercel 账号 | [vercel.com](https://vercel.com) | 托管 React 前端 |
| 阿里云域 | [wanwang.aliyun.com](https://wanwang.aliyun.com) | `zoewell.cn`，¥60/年 |
| DeepSeek Key | [platform.deepseek.com](https://platform.deepseek.com/api_keys) | LLM 调用 |

> **Railway 和 Vercel 都用 GitHub 登录。** 之后你在本地 `git push`，两边自动重新部署。

---

## 三、代码必须有的文件

部署前确认仓库根目录有这些文件：

```
adcockpit/
├── requirements.txt          ← Railway 靠它装 Python 依赖
├── railway.toml              ← Railway 启动命令
├── vercel.json               ← Vercel 构建配置
├── frontend/                 ← React 项目
│   ├── package.json
│   └── src/App.tsx
└── backend/
    └── app/api/main.py       ← FastAPI 入口
```

**`requirements.txt`**（根目录）：
```
fastapi>=0.110
uvicorn[standard]>=0.27
openai>=1.0
langgraph>=0.2
langchain>=0.2
langchain-openai>=0.1
pydantic>=2.0
httpx>=0.27
requests>=2.28
python-dotenv>=1.0
sse-starlette>=2.0
```

**`railway.toml`**（根目录）：
```toml
[build]

[deploy]
startCommand = "uvicorn backend.app.api.main:app --host 0.0.0.0 --port $PORT"

[service]
rootDirectory = "/"
```

> `rootDirectory` = `"/"`，不是 `"backend/"`——代码依赖根目录的 `tools/`，从根启动才能正确 import。

**`vercel.json`**（根目录）：
```json
{
  "framework": "vite",
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm ci",
  "rewrites": [
    { "source": "/((?!api).*)", "destination": "/index.html" }
  ]
}
```

---

## 四、后端部署：Railway

### 步骤

**1.** [railway.app](https://railway.app) → Login with GitHub

**2.** New Project → Deploy from GitHub Repo → 选你的 repo

**3.** Settings → Variables → 添加三个：

| Key | Value |
|-----|-------|
| `DEEPSEEK_API_KEY` | `sk-你的DeepSeek密钥` |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/v1` |
| `API_SECRET_KEY` | `adcockpit-demo-2026`（自定一个） |

> `API_SECRET_KEY` 是自己设的密码，留空 = 不验证。设了之后前端必须带相同的 key 才能调 API。

**4.** Networking → Generate Domain → 得到一个 `xxx.up.railway.app` 地址

**5.** 验证：浏览器打开 `https://xxx.up.railway.app/health` → 看到 `{"status":"ok"}`

### 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `railpack process exited` | 根目录缺 `requirements.txt` | 创建根目录 `requirements.txt` |
| `No start command detected` | 缺 `railway.toml` | 创建 `railway.toml` 指定 `startCommand` |
| 502 Bad Gateway | 启动命令错或端口错 | 检查 Settings → Start Command |
| DeepSeek Connection Error | Python 网络/代理问题 | Railway 是 Linux 通常没问题；如果还是不行，后端已实现 LLM 降级——用 Mock 数据跑完整流程 |

---

## 五、前端部署：Vercel

### 步骤

**1.** [vercel.com](https://vercel.com) → Login with GitHub

**2.** Add New → Project → 选你的 repo

**3.** ⚠️ **先别点 Deploy。** 做两个设置：

**Root Directory**：Settings → General → Root Directory → 填 `frontend` → Save

> 这个只能在 UI 设！写进 `vercel.json` 会报错 `should NOT have additional property "rootDirectory"`。

**Environment Variables**：Settings → Environment Variables → 添加：

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://xxx.up.railway.app`（Railway 给的域名） |
| `VITE_API_KEY` | `adcockpit-demo-2026`（和 Railway 的 `API_SECRET_KEY` 一致） |

> 不设 `VITE_API_URL` 的话，前端默认请求 `localhost:8000`——部署环境没有 localhost，全部 API 调失败。

**4.** 点 Deploy → 等 1-2 分钟 → 得到 `https://adcockpit-xxx.vercel.app`

**5.** 验证：浏览器打开，走完整优化流程（对话 → Trace 动画 → 审批 → 执行）

### 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `No FastAPI entrypoint found` | Vercel 检测到 Python，误判为 Python 项目 | `vercel.json` 加 `"framework": "vite"` |
| 前端 API 全失败 | `VITE_API_URL` 没设 | 设 Vercel 环境变量 |

---

## 六、阿里云域绑定（国内访问）

`*.vercel.app` 国内被墙，需要绑自己的域。

### 6.1 域名绑定 Vercel（前端）

**1.** Vercel → Settings → Domains → 添加 `adcockpit.zoewell.cn`

**2.** Vercel 提示 DNS 记录，去 [阿里云 DNS 解析](https://dns.console.aliyun.com) 添加：

| 记录类型 | 主机记录 | 记录值 |
|---------|---------|--------|
| CNAME | `adcockpit` | `cname.vercel-dns.com` |

**3.** 等 5-10 分钟生效 → 访问 `https://adcockpit.zoewell.cn` ✅

### 6.2 域名绑定 Railway（后端）

**1.** Railway → Settings → Custom Domain → 输入 `api.zoewell.cn` → Add

**2.** 弹窗显示 `DNS Target` ——复制这个值。去阿里云：

| 记录类型 | 主机记录 | 记录值 |
|---------|---------|--------|
| CNAME | `api` | Railway 弹窗里的 DNS Target |

**3.** 等生效 → 访问 `https://api.zoewell.cn/health` → `{"status":"ok"}`

**4.** 去 Vercel 把 `VITE_API_URL` 改成 `https://api.zoewell.cn`，重新 Deploy

### 6.3 最终效果

```
https://adcockpit.zoewell.cn     →  前端（国内正常访问，发给面试官）
https://api.zoewell.cn/health    →  后端（前端代码里默默用）
```

---

## 七、每次更新流程

日常改代码后：

```bash
git add -A
git commit -m "改了什么"
git push origin main
```

Vercel 和 Railway 自动检测推送、自动重新部署。不需要手动点。

---

## 八、部署踩坑全记录

| # | 报错 | 平台 | 原因 | 解决 |
|---|------|------|------|------|
| 1 | `railpack process exited with an error` | Railway | 根目录缺 `requirements.txt` | 项目根目录创建 `requirements.txt` |
| 2 | `No start command detected` | Railway | 缺 `railway.toml` | 创建 `railway.toml`，指定 `startCommand` |
| 3 | `ModuleNotFoundError`（运行时） | Railway | Root Directory 设了 `backend/` | 改为 `/` |
| 4 | `No FastAPI entrypoint found` | Vercel | 检测到 Python 文件，误判项目类型 | `vercel.json` 设 `"framework": "vite"` |
| 5 | `should NOT have rootDirectory` | Vercel | `vercel.json` 不支持这个字段 | 在 Vercel UI 的 Settings → General 里设 |
| 6 | 前端全部 API 请求失败 | Vercel | `VITE_API_URL` 没设，默认请求 localhost | Vercel 环境变量设 `VITE_API_URL` |
| 7 | 国内打不开 `*.vercel.app` | DNS | 该域大陆被墙 | 绑阿里云域，CNAME 到 `cname.vercel-dns.com` |
| 8 | Railway 域国内慢 | DNS | `up.railway.app` 无国内 CDN | 同样绑阿里云域解决 |

---

## 九、费用总结

| 项目 | 费用 | 备注 |
|------|------|------|
| GitHub | 免费 | |
| Railway | $5/月免费额度 | 512MB，够跑一整月 |
| Vercel | 免费 | 100GB 带宽/月 |
| 阿里云域 | ¥60/**年** | `zoewell.cn` |
| DeepSeek API | ¥0.5/千 tokens | 按量 |
| **合计** | **~¥60/年** | Demo 阶段几乎零成本 |
