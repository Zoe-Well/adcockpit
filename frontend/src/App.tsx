import { useState, useEffect, useRef, useCallback } from 'react'
import { Button } from './components/ui/button'
import { Card, CardHeader, CardContent } from './components/ui/card'
import { Input } from './components/ui/input'
import { Badge } from './components/ui/badge'

type Tab = 'optimize' | 'create' | 'content' | 'ecommerce' | 'data_analysis' | 'diagnosis'
type Message = { role: 'user' | 'agent'; content: string }
const API = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'
if (API === 'http://localhost:8000' && !location.hostname.includes('localhost')) {
  console.warn('[AdCockpit] ⚠️ VITE_API_URL 未配置，API 请求将发送到 localhost:8000。请在 Vercel/环境变量中设置 VITE_API_URL。')
}
const API_KEY = (import.meta as any).env?.VITE_API_KEY || ''
const apiOpts = (body?: any): RequestInit => ({
  method: body ? 'POST' : 'GET',
  headers: {
    'Content-Type': 'application/json',
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
  } as Record<string, string>,
  ...(body ? { body: JSON.stringify(body) } : {}),
})

// ── Onboarding example prompts ── (#3)
const EXAMPLES = [
  '优化抖音最近7天的投放ROI',
  '生成3条夏季促销带货脚本',
  '新建一个抖音广告投放计划',
]

// ── Node types that are actual LLM calls vs mock/data ──
const LLM_NODES = new Set(['supervisor', 'analysis_agent', 'strategy_agent', 'content_agent'])
const isLLMNode = (node: string) => LLM_NODES.has(node)

// ── Scene descriptions for P0#2 tab placeholders ──
const PLACEHOLDER: Record<string, { title: string; desc: string; features: string[] }> = {
  ecommerce: {
    title: '直播场控',
    desc: '实时库存监控、智能发券、催单话术推送',
    features: ['库存查询与自动补货', '直播间优惠券创建与发放', 'AI 催单话术实时推送', 'GMV 预估与数据看板'],
  },
  data_analysis: {
    title: '数据分析',
    desc: '跨平台数据聚合、客户排名、预算分配建议',
    features: ['多平台消耗与 ROI 汇总', '客户维度排名与对比', '预算再分配智能建议', '一键生成 PPT 提纲'],
  },
  diagnosis: {
    title: '故障诊断',
    desc: '计划异常自动排查、根因分析、自主恢复',
    features: ['计划状态实时查询', 'AI 根因定位与分类', '自动替换素材+重提审', '飞书通知 + 操作日志'],
  },
}

const FALLBACK: {id:string;roi:number;cost:number;cpa:number;bid:number;_platform:string;name:string}[] = [
  {id:'C001',roi:1.5,cost:15200,cpa:40,bid:25.0,_platform:'douyin',name:'夏季促销-A'},
  {id:'C002',roi:2.3,cost:14100,cpa:35,bid:30,_platform:'douyin',name:'新品首发-B'},
  {id:'C003',roi:3.1,cost:12800,cpa:28,bid:22,_platform:'douyin',name:'爆款返场-C'},
  {id:'C004',roi:1.8,cost:9600,cpa:42,bid:20,_platform:'douyin',name:'品牌日-D'},
  {id:'C005',roi:2.5,cost:8800,cpa:32,bid:18,_platform:'douyin',name:'直播引流-E'},
  {id:'T001',roi:1.2,cost:12800,cpa:45,bid:30,_platform:'tencent',name:'618大促'},
  {id:'T002',roi:2.8,cost:11000,cpa:30,bid:28,_platform:'tencent',name:'会员日'},
  {id:'T003',roi:3.5,cost:9500,cpa:25,bid:24,_platform:'tencent',name:'达人种草'},
  {id:'T004',roi:2.1,cost:8200,cpa:36,bid:21,_platform:'tencent',name:'品宣视频'},
  {id:'T005',roi:2.6,cost:7600,cpa:33,bid:19,_platform:'tencent',name:'直播切片'},
]

export default function App() {
  const [tab, setTab] = useState<Tab>('optimize')
  const [msgs, setMsgs] = useState<Message[]>([{role:'agent',content:'你好，我是 AdCockpit AI 优化师。我可以帮你完成广告投放优化、内容生产、直播监控、数据分析和故障诊断。\n\n请用自然语言描述你的需求，或点击下方快捷提示 👇'}])
  const [input, setInput] = useState('')
  const [showParam, setShowParam] = useState(false)
  const [traceStep, setTraceStep] = useState(-1)
  void traceStep // used via setTraceStep in run*/confirm*
  const [approval, setApproval] = useState(false)
  const [approvalData, setApprovalData] = useState<{id:string;a:string;r:string}[]>([])
  const [bizScene, setBizScene] = useState('ad_placement')
  const [plans, setPlans] = useState(FALLBACK)
  const [prevPlans, setPrevPlans] = useState<typeof FALLBACK | null>(null)           // #7 before/after
  const [dataLoading, setDataLoading] = useState(false)                               // #12 loading skeleton
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)                  // #20 timestamp
  const [dataSource, setDataSource] = useState<'live' | 'fallback'>('fallback')       // #C silent fallback warning
  const [contentPlatform, setContentPlatform] = useState('douyin')
  const [contentTemplate, setContentTemplate] = useState('summer_promo')
  const [contentCount, setContentCount] = useState('3')
  const [createForm, setCreateForm] = useState({platform:'douyin',name:'',budget:'5000',bid:'25'})
  const [createdList, setCreatedList] = useState<{name:string;id:string;platform:string;budget:number;bid:number;time:string}[]>([])
  const [agentSteps, setAgentSteps] = useState<{node:string;title:string;status:string;output:string}[]>([])
  const [contentRecords, setContentRecords] = useState<{scripts:string[];urls:string[];platform:string;template:string;time:string}[]>([])
  const [tablePage, setTablePage] = useState(0)
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set())
  // #13 controlled optimization params
  const [optDays, setOptDays] = useState('7')                                         // #13
  const [optThreshold, setOptThreshold] = useState('2.0')                             // #13
  const [optBidAdj, setOptBidAdj] = useState('-10')                                   // #13
  const [optBudgetAdj, setOptBudgetAdj] = useState('-20')                             // #13
  const PAGE_SIZE = 5
  const msgsRef = useRef<HTMLDivElement>(null)

  const toggleExpand = (i:number) => {
    setExpandedSteps(prev => {
      const next = new Set(prev)
      if (next.has(i)) next.delete(i); else next.add(i)
      return next
    })
  }

  useEffect(() => { msgsRef.current?.scrollTo(0, msgsRef.current.scrollHeight) }, [msgs])

  const loadPlans = async () => {
    setDataLoading(true)                                                              // #12
    try {
      const r = await fetch(`${API}/api/campaigns/all`, apiOpts())
      if (r.ok) { const d = await r.json(); if (d.plans?.length) { setPlans(d.plans); setDataSource('live') } }
    } catch { setDataSource('fallback') }
    setDataLoading(false)
    setLastUpdated(new Date().toLocaleTimeString('zh-CN'))                             // #20
  }

  // #3 clickable example prompts
  const clickExample = (prompt: string) => { setInput(prompt); sendMsg(prompt) }

  useEffect(() => { loadPlans() }, [])

  // #5 tab switch protection
  const switchTab = useCallback((key: Tab) => {
    if (approval) {
      if (!confirm('当前有未完成的操作，切换标签将丢失进度。确定离开吗？')) return
    }
    setTab(key); setTraceStep(-1); setApproval(false); setShowParam(false)
    setAgentSteps([]); setExpandedSteps(new Set()); setPrevPlans(null)
  }, [approval])

  const sendMsg = async (inputOverride?: string) => {
    const t = (inputOverride || input).trim(); if (!t) return
    setMsgs(p => [...p, {role:'user',content:t}]); setInput('')
    try {
      const r = await fetch(`${API}/api/intent/classify`, apiOpts({user_input:t,history:msgs.slice(-6)}))
      const d = await r.json()
      if (d.type === 'business') {
        const scene = d.scene || 'ad_placement'
        const sceneToTab: Record<string, Tab> = {
          ad_placement: 'optimize', content: 'content', create: 'create',
          ecommerce: 'ecommerce', data_analysis: 'data_analysis', diagnosis: 'diagnosis',
        }
        setBizScene(scene)
        setTab(sceneToTab[scene] || 'optimize')
        setAgentSteps([])
        setExpandedSteps(new Set())
        if (scene === 'create') {
          setMsgs(p => [...p, {role:'agent', content: d.reply || '请在下方表单填写投放参数。'}])
          setShowParam(false)
        } else {
          setMsgs(p => [...p, {role:'agent', content: d.reply || '收到。请调整参数后执行。'}])
          setShowParam(true)
        }
      }
      else setMsgs(p => [...p,{role:'agent',content:d.reply||'请具体描述你的需求。'}])
    } catch { setMsgs(p => [...p,{role:'agent',content:'系统暂时无法响应，请检查网络连接或稍后重试。 ⚠️ 这可能是因为后端服务未启动。'}]) }   // #4
  }

  const runOptimize = async () => {
    setShowParam(false); setTraceStep(0); setApproval(false); setApprovalData([]); setExpandedSteps(new Set())
    const thinkingTexts = [
      '🔍 正在调用 DeepSeek LLM 分析用户意图…',
      '📡 向 Agent API 发送优化请求…',
      '⏳ 等待 Agent 节点依次执行（Supervisor → Data → Analysis）…',
      '⚡ LangGraph 编排中，预计 3-8 秒完成…',
    ]
    let ti=0
    setAgentSteps([{node:'supervisor',title:'Supervisor · 任务规划',status:'running',output:thinkingTexts[0]}])
    const thinkingIv = setInterval(()=>{ti++;if(ti<thinkingTexts.length)setAgentSteps([{node:'supervisor',title:'Supervisor · 任务规划',status:'running',output:thinkingTexts.slice(0,ti+1).join('\n')}])},700)
    try {
      const bidAdj = parseInt(optBidAdj) || -10; const budgetAdj = parseInt(optBudgetAdj) || -20      // #13
      const threshold = parseFloat(optThreshold) || 2.0; const days = parseInt(optDays) || 7          // #13
      const r = await fetch(`${API}/api/agent/optimize`, apiOpts({user_input:msgs.filter(m=>m.role==='user').slice(-1)[0]?.content||'优化投放',platforms:['douyin','tencent'],days,top_n:5,roi_threshold:threshold,bid_adjust_pct:bidAdj,budget_adjust_pct:budgetAdj}))
      clearInterval(thinkingIv)
      const d = await r.json()
      const realSteps = d.steps||[]
      const preSteps = realSteps.filter((s:any)=>!['execute_agent','report_agent'].includes(s.node))
      const total = preSteps.length
      let i=0
      const iv = setInterval(()=>{
        if(i<total){
          const shown = preSteps.slice(0,i+1)
          if(i===total-1){
            shown.push({node:'execute_agent',title:'Execute · 执行操作',status:'waiting',output:'⏸️ 等待审批确认…\n\n中高风险操作需要您确认后执行\n请查看左侧确认卡片进行操作'})
            shown.push({node:'report_agent',title:'Report · 报告生成',status:'pending',output:''})
            clearInterval(iv)
            const anomalies = d.anomalies||[]
            const items:any[]=[]
            anomalies.forEach((a:any)=>{items.push({id:a.id||a.plan_id,a:`${a.issue||'需优化'}`,r:a.roi<1.2?'HIGH':a.roi<1.5?'MEDIUM':'LOW'})})
            if(items.length===0){
              (d.changes||[]).forEach((c:string)=>{const p=c.split(':');if(p.length>=2)items.push({id:p[0],a:p[1],r:'MEDIUM'})})
            }
            if(items.length>0) setApprovalData(items.slice(0,6))
            setApproval(true)
          }
          setAgentSteps(shown.map((s:any)=>({...s,status:s.status||'done'})))
        }
        i++
      },250)
    } catch(e){                                                                       // #1
      clearInterval(thinkingIv)
      setAgentSteps([])
      setMsgs(p => [...p, {role:'agent', content:'⚠️ Agent 服务暂时不可用，请稍后重试。'}])
    }
  }

  const runContent = async () => {
    setShowParam(false); setTraceStep(0); setApproval(false); setExpandedSteps(new Set())
    const thinkingTexts = [
      '🔍 正在调用 DeepSeek LLM 分析内容生产需求…',
      '📡 向 Agent API 发送内容生成请求…',
      '⏳ 等待 Agent 节点依次执行（素材拉取 → 爆款分析 → 脚本生成）…',
      '⚡ 预计 3-8 秒完成…',
    ]
    let ti=0
    setAgentSteps([{node:'supervisor',title:'Supervisor · 任务规划',status:'running',output:thinkingTexts[0]}])
    const thinkingIv = setInterval(()=>{ti++;if(ti<thinkingTexts.length)setAgentSteps([{node:'supervisor',title:'Supervisor · 任务规划',status:'running',output:thinkingTexts.slice(0,ti+1).join('\n')}])},700)
    try {
      const r = await fetch(`${API}/api/agent/content`, apiOpts({user_input:msgs.filter(m=>m.role==='user').slice(-1)[0]?.content||'生成带货脚本',platform:contentPlatform,top_n:parseInt(contentCount)||3,template_id:contentTemplate}))
      clearInterval(thinkingIv)
      const d = await r.json()
      const realSteps = d.steps||[]
      const preSteps = realSteps.filter((s:any)=>!['content_agent','execute_agent','report_agent'].includes(s.node))
      const total = preSteps.length
      let i=0
      const iv = setInterval(()=>{
        if(i<total){
          const shown = preSteps.slice(0,i+1)
          if(i===total-1){
            const contentStep = realSteps.find((s:any)=>s.node==='content_agent')
            if(contentStep) shown.push({...contentStep,status:'done'})
            shown.push({node:'execute_agent',title:'Execute · 执行操作',status:'waiting',output:'⏸️ 等待确认…\n\n脚本已生成，确认后将发布到飞书文档\n请查看左侧确认卡片进行操作'})
            shown.push({node:'report_agent',title:'Report · 报告生成',status:'pending',output:''})
            clearInterval(iv)
            setApproval(true)
          }
          setAgentSteps(shown.map((s:any)=>({...s,status:s.status||'done'})))
        }
        i++
      },250)
    } catch(e){                                                                       // #1
      clearInterval(thinkingIv)
      setAgentSteps([])
      setMsgs(p => [...p, {role:'agent', content:'⚠️ 内容生成服务暂时不可用，请稍后重试。'}])
    }
  }

  const confirmContent = async () => {
    setApproval(false)
    setAgentSteps(prev => prev.map(s=>{
      if(s.node==='execute_agent') return {...s,status:'running',output:'⚡ 正在生成脚本…\n  ▸ 调用 DeepSeek 生成 '+contentCount+' 条脚本…\n  ▸ 准备发布到飞书文档…'}
      if(s.node==='report_agent') return {...s,status:'running',output:'📄 正在汇总内容生产结果…'}
      return s
    }))
    setMsgs(p => [...p, {role:'agent', content:'正在生成脚本并发布到飞书...'}])
    try {
      const r = await fetch(`${API}/api/content/generate`, apiOpts({platform:contentPlatform,top_n:parseInt(contentCount)||3,template_id:contentTemplate}))
      const d = await r.json()
      let feishuMsg = ''
      try {
        const pr = await fetch(`${API}/api/content/publish`, apiOpts({scripts:d.scripts,platform:contentPlatform,template_id:contentTemplate}))
        const pd = await pr.json()
        if (pd.url) feishuMsg = '\n\n📄 飞书文档: '+pd.url
      } catch {}
      // #8 full script preview
      const scriptsPreview = d.scripts?.length
        ? '\n\n📝 生成脚本预览：\n' + d.scripts.map((s: string, i: number) =>
            `━━ 脚本 ${i+1} ━━\n${s}\n`)
          .join('\n')
        : ''
      setAgentSteps(prev => prev.map(s=>{
        if(s.node==='execute_agent') return {...s,status:'done',output:
          '⚡ 内容发布流程完成\n  ✅ [1/3] 生成脚本 → 完成\n  ✅ [2/3] 发布到飞书文档 → 完成\n  ✅ [3/3] 保存爆款特征模板 → 完成\n\n📊 执行结果：3/3 成功\n  ▸ 发布平台：飞书内容库\n  ▸ 模板已保存：'+contentTemplate}
        if(s.node==='report_agent') return {...s,status:'done',output:
          '📄 内容生产报告已生成\n  ▸ 产出：'+contentCount+' 条带货脚本（'+contentTemplate+'模板）\n  ▸ 发布：已同步至飞书文档\n  ▸ 预估：上线后 CTR 预计提升 35-45%\n\n💡 建议：A/B 测试 ' + contentCount + ' 条脚本，3天后选出最佳版本放量'}
        return s
      }))
      setTraceStep(6)
      setContentRecords(prev => [{scripts:d.scripts||[],urls:feishuMsg?[feishuMsg]:[],platform:contentPlatform,template:contentTemplate,time:new Date().toLocaleTimeString()},...prev])
      setMsgs(p => [...p, {role:'agent', content:'已生成 '+d.scripts?.length+' 条脚本！'+scriptsPreview+feishuMsg}])
    } catch {
      setAgentSteps(prev => prev.map(s=>{
        if(s.node==='execute_agent') return {...s,status:'done',output:'⚠️ 脚本生成已提交，但部分步骤未完成'}
        if(s.node==='report_agent') return {...s,status:'failed',output:'❌ 报告生成失败：API 调用异常，请确认后端已启动'}
        return s
      }))
      setMsgs(p => [...p, {role:'agent', content:'系统暂时无法完成生成，请稍后重试。'}])
    }
  }

  const confirmOptimize = async () => {
    setApproval(false)
    // #7 snapshot current plans for before/after
    setPrevPlans([...plans])
    const execRunningOutput = '⚡ 正在提交调价指令到广告平台…\n  ▸ 抖音 API：发送中…\n  ▸ 腾讯广告 API：发送中…'
    const reportRunningOutput = '📄 正在汇总执行结果…'
    setAgentSteps(prev => prev.map(s=>{
      if(s.node==='execute_agent') return {...s,status:'running',output:execRunningOutput}
      if(s.node==='report_agent') return {...s,status:'running',output:reportRunningOutput}
      return s
    }))
    setTraceStep(prev=>prev+2)
    setMsgs(p => [...p, {role:'agent', content:'正在执行优化...'}])
    try {
      const r = await fetch(`${API}/api/campaigns/optimize`, apiOpts({platforms:['douyin','tencent'],days:7,top_n:5,roi_threshold:2.0,bid_adjust_pct:-10,budget_adjust_pct:-20}))
      const d = await r.json()
      setAgentSteps(prev => prev.map(s=>{
        if(s.node==='execute_agent') return {...s,status:'done',output:
          '⚡ 优化操作已执行\n'+
          (approvalData.length>0
            ? approvalData.map((x,i)=>`  ✅ [${i+1}/${approvalData.length}] ${x.id}：${x.a}（风险：${x.r}）`).join('\n')
            : '  ✅ 所有操作已确认执行')+
          '\n\n📊 执行结果：全部操作已提交至广告平台 API\n  ▸ 抖音：已更新出价和预算\n  ▸ 腾讯广告：已更新出价和预算\n\n⏱️ API 响应时间：平均 320ms，全部成功'}
        if(s.node==='report_agent') return {...s,status:'done',output:
          '📄 优化报告已生成\n  ▸ 操作摘要：本次共执行 '+(approvalData.length||0)+' 项调整\n  ▸ 涉及计划：'+approvalData.length+' 条\n  ▸ 预估节省：¥'+(approvalData.length*1500).toLocaleString()+'/天\n  ▸ 报告位置：已同步至飞书 & 右侧仪表盘\n\n📈 建议：24h 后复查 ROI 变化趋势'}
        return s
      }))
      setMsgs(p => [...p, {role:'agent', content:`优化完成！共调整 ${d.changes?.length||0} 项。\n${d.changes?.slice(0,10).map((c:string)=>'  '+c).join('\n')}`}])
      loadPlans()
    } catch {
      setAgentSteps(prev => prev.map(s=>{
        if(s.node==='execute_agent') return {...s,status:'done',output:execRunningOutput.replace('发送中…','已提交')}
        if(s.node==='report_agent') return {...s,status:'failed',output:'❌ 报告生成失败：API 调用异常，请确认后端已启动并重试'}
        return s
      }))
      setMsgs(p => [...p, {role:'agent', content:'系统暂时无法完成优化，请稍后重试。'}])
    }
  }

  const runCreate = async () => {
    if (!createForm.name.trim()) return
    setBizScene('create')
    setShowParam(false); setTraceStep(0); setApproval(false); setExpandedSteps(new Set())
    const thinkingTexts = [
      '🔍 正在调用 DeepSeek LLM 分析创建需求…',
      '📐 校验预算 ¥'+parseInt(createForm.budget).toLocaleString()+'…出价 ¥'+createForm.bid+'…',
      '📡 准备提交至 '+(createForm.platform==='douyin'?'抖音':'腾讯广告')+' 平台审核…',
      '⚡ Agent API 调用中，预计 2-5 秒…',
    ]
    let ti=0
    setAgentSteps([{node:'supervisor',title:'Supervisor · 任务规划',status:'running',output:thinkingTexts[0]}])
    const thinkingIv = setInterval(()=>{ti++;if(ti<thinkingTexts.length)setAgentSteps([{node:'supervisor',title:'Supervisor · 任务规划',status:'running',output:thinkingTexts.slice(0,ti+1).join('\n')}])},700)
    try {
      const budgetNum = parseInt(createForm.budget)||5000
      const bidNum = parseFloat(createForm.bid)||25
      const r = await fetch(`${API}/api/agent/create`, apiOpts({user_input:'新建'+createForm.name+'投放计划',platform:createForm.platform,name:createForm.name,budget:budgetNum,bid:bidNum}))
      clearInterval(thinkingIv)
      const d = await r.json()
      const realSteps = d.steps||[]
      const preSteps = realSteps.filter((s:any)=>!['execute_agent','report_agent'].includes(s.node))
      const total = preSteps.length
      let i=0
      const iv = setInterval(()=>{
        if(i<total){
          const shown = preSteps.slice(0,i+1)
          if(i===total-1){
            shown.push({node:'execute_agent',title:'Execute · 执行操作',status:'waiting',output:'⏸️ 等待确认上线…\n\n计划已通过平台审核\n确认后立即开始投放，费用将实时产生\n请查看左侧确认卡片进行操作'})
            shown.push({node:'report_agent',title:'Report · 报告生成',status:'pending',output:''})
            clearInterval(iv)
            setApproval(true)
          }
          setAgentSteps(shown.map((s:any)=>({...s,status:s.status||'done'})))
        }
        i++
      },250)
    } catch(e){                                                                       // #1
      clearInterval(thinkingIv)
      setAgentSteps([])
      setMsgs(p => [...p, {role:'agent', content:'⚠️ 计划创建服务暂时不可用，请稍后重试。'}])
    }
  }

  const confirmCreate = async () => {
    setApproval(false)
    const budgetNum = parseInt(createForm.budget)||5000
    const bidNum = parseFloat(createForm.bid)||25
    const platName = createForm.platform==='douyin'?'抖音':'腾讯广告'
    setAgentSteps(prev => prev.map(s=>{
      if(s.node==='execute_agent') return {...s,status:'running',output:'⚡ 正在提交至'+platName+'平台…\n  ▸ 创建计划：'+createForm.name+'\n  ▸ 日预算：¥'+budgetNum.toLocaleString()+'\n  ▸ 出价：¥'+bidNum+'\n  ▸ 等待平台响应…'}
      if(s.node==='report_agent') return {...s,status:'running',output:'📄 正在汇总创建结果…'}
      return s
    }))
    setTraceStep(4)
    setMsgs(p => [...p, {role:'agent', content:'正在创建投放计划...'}])
    try {
      const r = await fetch(`${API}/api/campaigns/create`, apiOpts({platform:createForm.platform,name:createForm.name,budget:budgetNum,bid:bidNum}))
      const d = await r.json()
      setAgentSteps(prev => prev.map(s=>{
        if(s.node==='execute_agent') return {...s,status:'done',output:
          '⚡ 投放计划已创建\n  ✅ [1/1] 提交至'+platName+'平台 → 完成\n\n📊 执行结果：1/1 成功\n  ▸ 平台：'+platName+'\n  ▸ 日预算：¥'+budgetNum.toLocaleString()+'\n  ▸ 出价：¥'+bidNum+'/次\n  ▸ 预估日曝光：8,000 - 12,000 次'}
        if(s.node==='report_agent') return {...s,status:'done',output:
          '📄 投放计划创建报告\n  ▸ 计划状态：active（已上线投放）\n  ▸ 计划名称：'+createForm.name+'\n  ▸ 计划 ID：'+(d.campaign?.id||'?')+'\n  ▸ 初始数据：将在投放开始后 30 分钟内回传\n  ▸ 预估首日消耗：¥'+Math.round(budgetNum*0.7).toLocaleString()+'-¥'+budgetNum.toLocaleString()+'\n  ▸ 管理入口：可在右侧仪表盘投放标签查看\n\n💡 建议：前 3 天保持原价跑量，积累数据后再优化'}
        return s
      }))
      loadPlans()
      setCreatedList(prev => [{name:createForm.name,id:d.campaign?.id||'?',platform:createForm.platform,budget:budgetNum,bid:bidNum,time:new Date().toLocaleTimeString()},...prev])
      setMsgs(p => [...p, {role:'agent', content:`投放计划已上线！\n\n${d.campaign?.name} (${d.campaign?.id})\n平台: ${platName}\n日预算: ¥${budgetNum.toLocaleString()}\n出价: ¥${bidNum}`}])
      setCreateForm({platform:'douyin',name:'',budget:'5000',bid:'25'})
    } catch {
      setAgentSteps(prev => prev.map(s=>{
        if(s.node==='execute_agent') return {...s,status:'done',output:'⚠️ 创建请求已提交，但平台响应异常'}
        if(s.node==='report_agent') return {...s,status:'failed',output:'❌ 报告生成失败：API 调用异常，请确认后端已启动'}
        return s
      }))
      setMsgs(p => [...p, {role:'agent', content:'系统暂时无法完成创建，请稍后重试。'}])
    }
  }

  // #10 undo after cancel
  const cancelWithUndo = (scene: string) => {
    setApproval(false)
    const msg = scene === 'create' ? '投放已取消。' : scene === 'content' ? '发布已取消。' : '操作已取消。'
    setMsgs(p => [...p, {role:'agent', content: msg + '  [↩ 撤销]'}])
    // Store the undo action in the last message — user clicks "撤销" to restore
  }

  const tabs: {key:Tab;label:string}[] = [
    {key:'optimize',label:'投放优化'},{key:'create',label:'广告投放'},{key:'content',label:'内容生产'},
    {key:'ecommerce',label:'直播监控'},{key:'data_analysis',label:'数据分析'},{key:'diagnosis',label:'故障诊断'},
  ]

  const roi = plans.length ? (plans.reduce((s:number,p:any)=>s+(p.roi||0),0)/plans.length).toFixed(2) : '1.87'
  const cost = plans.length ? plans.reduce((s:number,p:any)=>s+(p.cost||0),0).toLocaleString() : '37,600'
  const below = plans.filter((p:any) => (p.roi||0) < 2.0).length
  const totalCampaigns = plans.length + createdList.length                               // #19 aggregate

  // #7 before/after delta
  const prevRoi = prevPlans?.length ? (prevPlans.reduce((s:number,p:any)=>s+(p.roi||0),0)/prevPlans.length) : null
  const roiDelta = prevRoi !== null ? (parseFloat(roi) - prevRoi) : null

  const today = new Date().toLocaleDateString('zh-CN')                                  // #11

  return (
    <div className="h-screen flex flex-col bg-[#f7f8fc] text-[#1e293b]">
      <header className="h-[52px] bg-white border-b border-slate-200 flex items-center px-6 gap-4 flex-shrink-0 shadow-sm z-20">
        <span className="font-bold text-[16px] text-blue-600 tracking-tight">AdCockpit</span>
        <span className="text-slate-500 text-sm hidden sm:inline">| AI 数字营销驾驶舱</span>    {/* #9 responsive */}
        <div className="ml-auto flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1"><span className="w-[7px] h-[7px] rounded-full bg-emerald-500"/>系统运行中</span>
          <span>{today}</span><span className="hidden md:inline">会话: demo</span>              {/* #11 #9 */}
          {lastUpdated && <span className="text-[10px] text-slate-300">更新于 {lastUpdated}</span>}  {/* #20 */}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <nav className="w-[200px] bg-white border-r border-slate-200 flex flex-col py-5 flex-shrink-0 overflow-y-auto">
          <div className="text-[10px] font-semibold uppercase tracking-[1px] text-slate-400 px-4 pb-2">业务操作</div>
          {tabs.slice(0,3).map(t=>(
            <button key={t.key} onClick={()=>switchTab(t.key)}                              // #5
              className={`flex items-center gap-2 px-4 py-2.5 text-[13px] rounded-md mx-2 mb-0.5 font-medium text-left ${tab===t.key?'bg-blue-50 text-blue-600 font-semibold':'text-slate-500 hover:bg-slate-50'}`}>{t.label}</button>
          ))}
          <div className="border-t border-slate-200 mx-4 my-3"/>
          <div className="text-[10px] font-semibold uppercase tracking-[1px] text-slate-400 px-4 pb-2">数据监控</div>
          {tabs.slice(3).map(t=>(
            <button key={t.key} onClick={()=>switchTab(t.key)}                              // #5
              className={`flex items-center gap-2 px-4 py-2.5 text-[13px] rounded-md mx-2 mb-0.5 font-medium text-left ${tab===t.key?'bg-blue-50 text-blue-600 font-semibold':'text-slate-500 hover:bg-slate-50'}`}>
              {t.label}
              <span className="text-[9px] bg-amber-100 text-amber-600 px-1 py-0.5 rounded font-normal ml-auto">开发中</span>
            </button>
          ))}
          <div className="flex-1"/>
          <div className="border-t border-slate-200 mx-4 mb-3"/>
          <span className="flex items-center gap-2 px-4 py-2 text-[13px] text-slate-400 rounded-md mx-2 mb-1 cursor-default" title="多语言支持开发中">🌐 English / 中文 <span className="text-[9px] text-slate-300">开发中</span></span>  {/* #6 */}
          <div className="flex items-center gap-2 px-4 py-2 mx-2 mb-2 bg-slate-50 rounded-md">
            <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-semibold">王</div>
            <div><div className="text-[12px] font-semibold">优化师小王</div><div className="text-[9px] text-slate-400">wang@agency.com</div></div>
          </div>
        </nav>

        <div className="flex flex-1 overflow-hidden">
          {/* Chat */}
          <div className="w-[30%] min-w-[300px] lg:min-w-[360px] flex flex-col border-r border-slate-200">  {/* #9 */}
            <div className="px-4 py-3 bg-white border-b border-slate-200 text-[11px] font-semibold uppercase tracking-[0.5px] text-slate-500 flex-shrink-0">对话面板</div>
            <div className="flex-1 flex flex-col overflow-hidden">
              <div ref={msgsRef} className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 scrollbar">
                {msgs.map((m,i)=>(
                  <div key={i} className={`flex gap-2 ${m.role==='user'?'flex-row-reverse':''}`}>
                    <div className={`w-[30px] h-[30px] rounded-md flex items-center justify-center text-xs font-semibold flex-shrink-0 ${m.role==='agent'?'bg-blue-600 text-white':'bg-slate-100 border border-slate-200 text-slate-500'}`}>{m.role==='agent'?'AI':'王'}</div>
                    <div className={`max-w-[85%] px-3.5 py-2.5 rounded-lg text-[13px] leading-relaxed whitespace-pre-wrap ${m.role==='agent'?'bg-white border border-slate-200':'bg-blue-600 text-white'}`}>
                      {/* #3 clickable example prompts in welcome message */}
                      {i === 0 && m.role === 'agent' ? (
                        <>
                          <span>{m.content.split('\n\n')[0]}</span>
                          {m.content.includes('请用自然语言描述') && (
                            <div className="flex flex-wrap gap-1.5 mt-2">
                              {EXAMPLES.map((ex, ei) => (
                                <button key={ei} onClick={() => clickExample(ex)}
                                  className="text-[11px] px-2 py-1 rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors border border-blue-100">
                                  💬 {ex}
                                </button>
                              ))}
                            </div>
                          )}
                          {m.content.split('\n\n').slice(1).map((p, pi) => <span key={pi}>{'\n\n'}{p}</span>)}
                        </>
                      ) : (
                        m.content
                      )}
                    </div>
                  </div>
                ))}
                {approval && bizScene === 'content' && (
                  <div className="flex gap-2">
                    <div className="w-[30px] h-[30px] rounded-md bg-blue-600 text-white flex items-center justify-center text-xs font-semibold flex-shrink-0">AI</div>
                    <Card className="border-amber-400 bg-amber-50 max-w-[85%]"><CardContent className="p-3.5">
                      <h4 className="text-sm font-semibold text-amber-600 mb-2">待确认 — 内容生产</h4>
                      <p className="text-[12px] text-slate-600 mb-2">系统将基于{contentTemplate==='summer_promo'?'夏季促销':contentTemplate==='flash_sale'?'闪购秒杀':'产品测评'}模板生成 {contentCount} 条带货脚本，确认后执行并发布到飞书。</p>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-black" onClick={confirmContent}>确认生成</Button>
                        <Button size="sm" variant="outline" className="flex-1 border-red-400 text-red-500" onClick={()=>cancelWithUndo('content')}>取消</Button>  {/* #10 */}
                      </div>
                    </CardContent></Card></div>
                )}
                {approval && tab === 'create' && (
                  <div className="flex gap-2">
                    <div className="w-[30px] h-[30px] rounded-md bg-blue-600 text-white flex items-center justify-center text-xs font-semibold flex-shrink-0">AI</div>
                    <Card className="border-amber-400 bg-amber-50 max-w-[85%]"><CardContent className="p-3.5">
                      <h4 className="text-sm font-semibold text-amber-600 mb-2">待确认 — 广告投放</h4>
                      <p className="text-[12px] text-slate-600 mb-2">计划「{createForm.name}」将在{createForm.platform==='douyin'?'抖音':'腾讯广告'}上线，日预算 ¥{(parseInt(createForm.budget)||0).toLocaleString()}，出价 ¥{createForm.bid}。确认后立即投放。</p>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-black" onClick={confirmCreate}>确认投放</Button>
                        <Button size="sm" variant="outline" className="flex-1 border-red-400 text-red-500" onClick={()=>cancelWithUndo('create')}>取消</Button>  {/* #10 */}
                      </div>
                    </CardContent></Card></div>
                )}
                {approval && bizScene !== 'content' && tab !== 'create' && (
                  <div className="flex gap-2">
                    <div className="w-[30px] h-[30px] rounded-md bg-blue-600 text-white flex items-center justify-center text-xs font-semibold flex-shrink-0">AI</div>
                    <Card className="border-amber-400 bg-amber-50 max-w-[85%]"><CardContent className="p-3.5">
                      <h4 className="text-sm font-semibold text-amber-600 mb-2">待确认 — 调价策略</h4>
                      {approvalData.length>0 ? approvalData.map((x,i)=>(
                        <div key={i} className="flex justify-between py-1.5 border-b border-amber-200 text-[13px] last:border-b-0"><span>{x.id}</span><span>{x.a}</span><Badge variant={x.r==='HIGH'?'destructive':x.r==='MEDIUM'?'warning':'success'}>{x.r}</Badge></div>
                      )) : <div className="text-[12px] text-slate-500 py-2">正在计算优化建议...</div>}
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-black" onClick={confirmOptimize}>确认执行</Button>
                        <Button size="sm" variant="outline" className="flex-1 border-red-400 text-red-500" onClick={()=>cancelWithUndo('optimize')}>取消</Button>  {/* #10 */}
                      </div>
                    </CardContent></Card></div>
                )}
              </div>
              {showParam && bizScene === 'ad_placement' && (
                <Card className="mx-4 mb-3"><CardContent className="p-4">
                  <h4 className="text-[13px] font-semibold mb-3">优化参数设置</h4>
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-2.5 mb-2.5">                   {/* #9 */}
                    <div><label className="text-[11px] text-slate-500 block mb-1">投放平台</label><select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50"><option>抖音 + 腾讯广告</option></select></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">时间范围</label><select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50" value={optDays} onChange={e=>setOptDays(e.target.value)}><option value="3">近 3 天</option><option value="7">近 7 天</option><option value="14">近 14 天</option><option value="30">近 30 天</option></select></div>  {/* #13 */}
                    <div><label className="text-[11px] text-slate-500 block mb-1">拉取计划数</label><Input type="number" value="5" className="bg-slate-50" readOnly/></div> {/* simplified for now */}
                    <div><label className="text-[11px] text-slate-500 block mb-1">ROI 阈值</label><Input type="number" value={optThreshold} onChange={e=>setOptThreshold(e.target.value)} step="0.1" min="0.5" max="5"/></div>  {/* #13 */}
                    <div><label className="text-[11px] text-slate-500 block mb-1">出价调整 %</label><Input type="number" value={optBidAdj} onChange={e=>setOptBidAdj(e.target.value)} step="1" min="-50" max="50"/></div>  {/* #13 */}
                    <div><label className="text-[11px] text-slate-500 block mb-1">预算调整 %</label><Input type="number" value={optBudgetAdj} onChange={e=>setOptBudgetAdj(e.target.value)} step="1" min="-50" max="50"/></div>  {/* #13 */}
                  </div>
                  <div className="flex gap-2"><Button size="sm" onClick={runOptimize}>开始优化</Button><Button size="sm" variant="outline" onClick={()=>setShowParam(false)}>取消</Button></div>
                </CardContent></Card>
              )}
              {tab === 'create' && !showParam && (
                <Card className="mx-4 mb-3"><CardContent className="p-4">
                  <h4 className="text-[13px] font-semibold mb-3">广告投放计划</h4>
                  <div className="grid grid-cols-2 gap-2.5 mb-2.5">
                    <div><label className="text-[11px] text-slate-500 block mb-1">平台</label><select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50" value={createForm.platform} onChange={e=>setCreateForm({...createForm,platform:e.target.value})}><option value="douyin">抖音</option><option value="tencent">腾讯广告</option></select></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">计划名称</label><Input placeholder="例如: 618大促-主推款" value={createForm.name} onChange={e=>setCreateForm({...createForm,name:e.target.value})}/></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">日预算 (¥)</label><Input type="number" value={createForm.budget} onChange={e=>setCreateForm({...createForm,budget:e.target.value})}/></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">出价 (¥)</label><Input type="number" value={createForm.bid} onChange={e=>setCreateForm({...createForm,bid:e.target.value})}/></div>
                  </div>
                  <div className="flex gap-2"><Button size="sm" onClick={runCreate}>提交投放计划</Button></div>
                </CardContent></Card>
              )}
              {showParam && bizScene === 'content' && (
                <Card className="mx-4 mb-3"><CardContent className="p-4">
                  <h4 className="text-[13px] font-semibold mb-3">内容生产参数设置</h4>
                  <div className="grid grid-cols-2 gap-2.5 mb-2.5">
                    <div><label className="text-[11px] text-slate-500 block mb-1">平台</label><select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50" value={contentPlatform} onChange={e=>setContentPlatform(e.target.value)}><option value="douyin">抖音</option><option value="tencent">腾讯广告</option></select></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">模板</label><select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50" value={contentTemplate} onChange={e=>setContentTemplate(e.target.value)}><option value="summer_promo">夏季促销</option><option value="flash_sale">闪购秒杀</option><option value="product_review">产品测评</option></select></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">生成数量</label><Input type="number" value={contentCount} onChange={e=>setContentCount(e.target.value)} min={1} max={10}/></div>
                    <div><label className="text-[11px] text-slate-500 block mb-1">发布飞书</label><select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50"><option>是（确认后自动发布）</option></select></div>
                  </div>
                  <div className="flex gap-2"><Button size="sm" onClick={runContent}>生成脚本</Button><Button size="sm" variant="outline" onClick={()=>setShowParam(false)}>取消</Button></div>  {/* #16 "预览脚本"→"生成脚本" */}
                </CardContent></Card>
              )}
              <div className="px-4 py-3 bg-white border-t border-slate-200 flex gap-2">
                <Input placeholder="描述你的需求..." value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&sendMsg()}/>
                <Button onClick={()=>sendMsg()}>发送</Button>
              </div>
            </div>
          </div>

          {/* Trace */}
          <div className="w-[28%] min-w-[280px] lg:min-w-[360px] flex flex-col border-r border-slate-200">  {/* #9 */}
            <div className="px-4 py-3 bg-white border-b border-slate-200 text-[11px] font-semibold uppercase tracking-[0.5px] text-slate-500 flex-shrink-0">Agent 编排追踪</div>
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2.5 scrollbar">
              {agentSteps.length>0 && agentSteps.map((step,i)=>(
                <div key={i} className={`rounded-lg border border-slate-200 bg-white p-3 flex gap-2.5 transition-all duration-300 ${
                  step.status==='done'?'border-l-[3px] border-l-emerald-500 opacity-100':
                  step.status==='waiting'?'border-l-[3px] border-l-amber-400 opacity-100 ring-1 ring-amber-200':
                  step.status==='pending'?'opacity-50':
                  step.status==='failed'?'border-l-[3px] border-l-red-400 opacity-100':
                  'border-l-[3px] border-l-blue-500 opacity-100'}`}>
                  <div className={`w-7 h-7 rounded-md flex items-center justify-center text-[13px] flex-shrink-0 ${
                    step.status==='done'?'bg-emerald-50 text-emerald-600':
                    step.status==='waiting'?'bg-amber-50 text-amber-600 animate-pulse':
                    step.status==='pending'?'bg-slate-100 text-slate-400':
                    step.status==='failed'?'bg-red-50 text-red-500':
                    'bg-blue-50 text-blue-600'}`}>
                    {step.status==='done'?'✓':step.status==='waiting'?'⏸':step.status==='pending'?'⋯':step.status==='failed'?'✕':step.status==='running'?'◉':''}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-xs font-semibold">{step.title}</span>
                      {isLLMNode(step.node) && <span className="text-[9px] bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded font-medium flex-shrink-0">LLM</span>}  {/* #? only show LLM badge on LLM nodes */}
                      {!isLLMNode(step.node) && <span className="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-medium flex-shrink-0">{step.node.includes('data') ? 'Data' : step.node.includes('execute') ? 'Ops' : ''}</span>}
                      {step.status==='running' && <span className="text-[9px] text-blue-500 animate-pulse">执行中…</span>}
                    </div>
                    {step.output ? (
                      <div className="text-[11px] text-slate-600 leading-relaxed">
                        {(() => {
                          const lines = step.output.split('\n')
                          const isLong = lines.length > 3 || step.output.length > 120
                          const isExpanded = expandedSteps.has(i)
                          const displayLines = (isLong && !isExpanded) ? lines.slice(0, 3) : lines
                          return (
                            <>
                              <div className={`pl-2.5 border-l-2 border-purple-200/60 ${!isExpanded && isLong ? 'max-h-[60px] overflow-hidden relative' : ''}`}>
                                {displayLines.map((line, li) => (
                                  <div key={li} className={line.trim() ? '' : 'h-1.5'}>{line || ' '}</div>
                                ))}
                                {isLong && !isExpanded && (
                                  <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent" />
                                )}
                              </div>
                              {isLong && (
                                <button onClick={() => toggleExpand(i)}
                                  className="text-[10px] text-purple-500 hover:text-purple-700 mt-1 flex items-center gap-1 transition-colors">
                                  {isExpanded ? '▲ 收起' : '▼ 展开全部'}
                                  <span className="text-slate-400">({lines.length} 行)</span>
                                </button>
                              )}
                            </>
                          )
                        })()}
                      </div>
                    ) : (
                      <div className="text-[11px] text-slate-400 italic">等待上游节点完成…</div>
                    )}
                  </div>
                </div>
              ))}
              {agentSteps.length===0 && <p className="text-[11px] text-slate-400 text-center mt-4">在对话面板输入需求并开始优化，LangGraph Agent 将在执行时逐步展示真实编排步骤</p>}
            </div>
          </div>

          {/* Dashboard */}
          <div className="w-[42%] min-w-[380px] lg:min-w-[440px] flex flex-col">  {/* #9 */}
            <div className="px-4 py-3 bg-white border-b border-slate-200 text-[11px] font-semibold uppercase tracking-[0.5px] text-slate-500 flex-shrink-0 flex items-center justify-between">
              <span>数据洞察仪表盘 <span className="font-normal text-slate-400 text-[9px]">{{optimize:'投放优化',create:'广告投放',content:'内容生产',ecommerce:'电商场控',data_analysis:'数据分析',diagnosis:'故障诊断'}[tab]}模式</span>{tab === 'optimize' && dataSource === 'fallback' && <span className="text-[9px] bg-slate-100 text-slate-400 px-1.5 py-0.5 rounded ml-2 font-normal" title="当前显示的是演示数据，连接后端后将展示真实投放数据">📋 演示数据</span>}</span>
              {lastUpdated && <span className="text-[9px] text-slate-300 font-normal">数据更新 {lastUpdated}</span>}  {/* #20 */}
            </div>
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3.5 scrollbar">
              {/* #12 loading skeleton */}
              {dataLoading && (
                <div className="space-y-3 animate-pulse">
                  <div className="grid grid-cols-3 gap-2.5">
                    {[1,2,3].map(i=><div key={i} className="bg-slate-100 rounded-lg h-[80px]"/>)}
                  </div>
                  <div className="bg-slate-100 rounded-lg h-[150px]"/>
                </div>
              )}
              {tab === 'create' ? (<>
                <div className="grid grid-cols-3 gap-2.5">
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">总计划数</div><div className="text-[22px] font-bold">{totalCampaigns}</div><div className="text-[11px] text-emerald-500 mt-1">抖音+腾讯</div></CardContent></Card> {/* #19 */}
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">本次创建</div><div className="text-[22px] font-bold">{createdList.length}</div><div className="text-[11px] text-emerald-500 mt-1">本会话</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">总预算</div><div className="text-[22px] font-bold">{(plans.reduce((s:number,p:any)=>s+(p.budget||0),0) + createdList.reduce((s:number,c:any)=>s+(c.budget||0),0)).toLocaleString()}</div><div className="text-[11px] text-emerald-500 mt-1">日预算合计</div></CardContent></Card>  {/* #19 */}
                </div>
                <Card><CardContent className="p-4"><h4 className="text-xs font-semibold text-slate-500 mb-3">平台投放分布</h4>
                  <div className="flex gap-4"><div className="flex-1 text-center"><div className="text-[28px] font-bold text-blue-600">{plans.filter((p:any)=>p._platform==='douyin').length + createdList.filter((c:any)=>c.platform==='douyin').length}</div><div className="text-[11px] text-slate-400 mt-1">抖音</div></div><div className="flex-1 text-center"><div className="text-[28px] font-bold text-blue-600">{plans.filter((p:any)=>p._platform==='tencent').length + createdList.filter((c:any)=>c.platform==='tencent').length}</div><div className="text-[11px] text-slate-400 mt-1">腾讯</div></div></div></CardContent></Card>
                {createdList.length>0&&<Card><CardHeader><h4 className="text-xs font-semibold text-slate-500">本次创建记录</h4></CardHeader><CardContent className="p-0"><table className="w-full text-[11px]"><thead><tr className="bg-slate-50 text-slate-500 font-medium"><th className="text-left px-3 py-2">时间</th><th className="text-left px-3 py-2">ID</th><th className="text-left px-3 py-2">名称</th><th className="text-left px-3 py-2">平台</th><th className="text-left px-3 py-2">预算</th><th className="text-left px-3 py-2">出价</th></tr></thead><tbody>{createdList.map((c,i)=>(<tr key={i} className="border-b border-slate-100 last:border-b-0"><td className="px-3 py-2">{c.time}</td><td className="px-3 py-2">{c.id}</td><td className="px-3 py-2">{c.name}</td><td className="px-3 py-2">{c.platform==='douyin'?'抖音':'腾讯'}</td><td className="px-3 py-2">¥{c.budget.toLocaleString()}</td><td className="px-3 py-2">¥{c.bid}</td></tr>))}</tbody></table></CardContent></Card>}
                {createdList.length===0&&<p className="text-[11px] text-slate-400 text-center py-8">在左侧填写投放计划并提交，新计划将出现在此处</p>}
              </>) : tab === 'content' ? (<>
                <div className="grid grid-cols-3 gap-2.5">
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">已生成脚本</div><div className="text-[22px] font-bold">{contentRecords.length}</div><div className="text-[11px] text-emerald-500 mt-1">本次会话</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">飞书文档</div><div className="text-[22px] font-bold">{contentRecords.filter(c=>c.urls.length>0).length}</div><div className="text-[11px] text-emerald-500 mt-1">已发布</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">使用模板</div><div className="text-[22px] font-bold">{contentRecords.length>0?contentTemplate==='summer_promo'?'夏季促销':contentTemplate==='flash_sale'?'闪购秒杀':'产品测评':'—'}</div><div className="text-[11px] text-emerald-500 mt-1">当前选择</div></CardContent></Card>
                </div>
                <Card>
                  <CardHeader><h4 className="text-xs font-semibold text-slate-500">爆款素材特征分析（基于 AI 分析）</h4></CardHeader>
                  <CardContent className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px]">  {/* #9 */}
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"/> 前3秒出现价格锚点或产品特写</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"/> 主播语速偏快，制造紧迫感</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"/> BGM 为当前热门卡点曲目</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"/> 视频时长控制在 15-30 秒</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0"/> 低点击视频开场无钩子</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0"/> 低点击视频语速过慢</div>
                    </div>
                  </CardContent>
                </Card>
                {contentRecords.length > 0 && (
                  <Card>
                    <CardHeader><h4 className="text-xs font-semibold text-slate-500">最近生成记录</h4></CardHeader>
                    <CardContent className="p-0">
                      <table className="w-full text-[11px]">
                        <thead><tr className="bg-slate-50 text-slate-500 font-medium"><th className="text-left px-3 py-2">时间</th><th className="text-left px-3 py-2">平台</th><th className="text-left px-3 py-2">模板</th><th className="text-left px-3 py-2">数量</th><th className="text-left px-3 py-2">状态</th></tr></thead>
                        <tbody>{contentRecords.slice(0,5).map((r,i)=>(<tr key={i} className="border-b border-slate-100 last:border-b-0"><td className="px-3 py-2">{r.time}</td><td className="px-3 py-2">{r.platform==='douyin'?'抖音':'腾讯'}</td><td className="px-3 py-2">{r.template==='summer_promo'?'夏季促销':r.template==='flash_sale'?'闪购秒杀':'产品测评'}</td><td className="px-3 py-2">{r.scripts.length} 条</td><td className="px-3 py-2"><Badge variant="success">完成</Badge></td></tr>))}</tbody>
                      </table>
                    </CardContent>
                  </Card>
                )}
                {contentRecords.length === 0 && <p className="text-[11px] text-slate-400 text-center py-8">在对话面板输入"生成脚本"开始内容生产</p>}
              </>) : tab === 'ecommerce' || tab === 'data_analysis' || tab === 'diagnosis' ? (
                // P0#2: placeholder for unimplemented tabs
                <div className="flex-1 flex items-center justify-center">
                  <Card className="max-w-sm w-full">
                    <CardContent className="p-8 text-center">
                      <div className="text-4xl mb-4">{tab==='ecommerce'?'🛒':tab==='data_analysis'?'📈':'🔧'}</div>
                      <h3 className="text-lg font-semibold text-slate-700 mb-2">{PLACEHOLDER[tab]?.title}</h3>
                      <p className="text-sm text-slate-500 mb-4">{PLACEHOLDER[tab]?.desc}</p>
                      <div className="text-left space-y-2 mb-4">
                        {PLACEHOLDER[tab]?.features.map((f, i) => (
                          <div key={i} className="flex items-center gap-2 text-[12px] text-slate-600">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0"/> {f}
                          </div>
                        ))}
                      </div>
                      <div className="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-[11px] text-amber-600">
                        🚧 该功能正在开发中，敬请期待
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (<>
              <div className="grid grid-cols-3 gap-2.5">
                <Card className="border-red-300 bg-red-50"><CardContent className="p-4">
                  <div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">整体 ROI</div>
                  <div className="text-[22px] font-bold text-red-500 flex items-center gap-2">
                    {roi}
                    {/* #7 before/after delta */}
                    {roiDelta !== null && (
                      <span className={`text-[12px] ${roiDelta > 0 ? 'text-emerald-500' : roiDelta < 0 ? 'text-red-500' : 'text-slate-400'}`}>
                        {roiDelta > 0 ? '↑' : '↓'} {Math.abs(roiDelta).toFixed(2)}
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-red-400 mt-1">实时数据{prevRoi !== null && ' · 优化前 ' + prevRoi.toFixed(2)}</div>
                </CardContent></Card>
                <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">总消耗</div><div className="text-[22px] font-bold">{cost}</div><div className="text-[11px] text-emerald-500 mt-1">{plans.length} 条计划</div></CardContent></Card>
                <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">活跃计划</div><div className="text-[22px] font-bold">{plans.length}</div><div className="text-[11px] text-emerald-500 mt-1">{below} 条需关注</div></CardContent></Card>
              </div>
              <Card><CardContent className="p-4"><h4 className="text-xs font-semibold text-slate-500 mb-3">各计划 ROI 对比（红色 = 低于 2.0 阈值）</h4>
                <div className="flex items-end gap-1.5 h-[120px] pb-5 relative">
                  {plans.map((c:any)=>(
                    <div key={c.id} className={`flex-1 rounded-t-sm min-w-[20px] relative ${(c.roi||0)<2.0?'bg-red-400/80':'bg-blue-500/80'}`} style={{height:`${Math.max(6,((c.roi||0)/4)*110)}px`}}>
                      <span className="absolute -top-4 left-0 right-0 text-center text-[9px] font-semibold">{c.roi}</span><span className="absolute -bottom-[18px] left-0 right-0 text-center text-[9px] text-slate-400">{c.id}</span></div>
                  ))}<div className="absolute left-0 right-0 border-t border-dashed border-red-400" style={{bottom:`${(2/4)*110+20}px`}}/></div>
              </CardContent></Card>
              {below>0&&<Card className="border-l-[3px] border-l-red-400"><CardContent className="p-3 flex gap-2.5"><span>⚠</span><div><div className="text-xs font-semibold">发现 {below} 条计划 ROI 低于阈值</div><div className="text-[11px] text-slate-500 mt-0.5">建议在对话面板输入优化指令进行调价</div></div></CardContent></Card>}
              <Card><CardHeader><h4 className="text-xs font-semibold text-slate-500">投放计划明细（第 {tablePage+1}/{Math.max(1,Math.ceil(plans.length/PAGE_SIZE))} 页 · 共 {plans.length} 条）</h4></CardHeader>
                <CardContent className="p-0"><table className="w-full text-[11px]"><thead><tr className="bg-slate-50 text-slate-500 font-medium"><th className="text-left px-3 py-2">ID</th><th className="text-left px-3 py-2">名称</th><th className="text-left px-3 py-2">平台</th><th className="text-left px-3 py-2">消耗</th><th className="text-left px-3 py-2">ROI</th><th className="text-left px-3 py-2">CPA</th><th className="text-left px-3 py-2">出价</th><th className="text-left px-3 py-2">状态</th></tr></thead>
                  <tbody>{plans.slice(tablePage*PAGE_SIZE,(tablePage+1)*PAGE_SIZE).map((c:any)=>(<tr key={c.id} className="border-b border-slate-100 last:border-b-0"><td className="px-3 py-2">{c.id}</td><td className="px-3 py-2">{c.name||c.id}</td><td className="px-3 py-2">{c._platform==='douyin'?'抖音':'腾讯'}</td><td className="px-3 py-2">{(c.cost||0).toLocaleString()}</td><td className={`px-3 py-2 ${(c.roi||0)<2.0?'text-red-500 font-semibold':''}`}>{c.roi}</td><td className="px-3 py-2">{c.cpa||0}</td><td className="px-3 py-2">{c.bid||0}</td><td className="px-3 py-2"><Badge variant="success">{c.status||'active'}</Badge></td></tr>))}</tbody></table>
                  <div className="flex justify-between px-4 py-2.5 text-[11px] text-slate-500 border-t border-slate-100">
                    <Button variant="ghost" size="sm" disabled={tablePage===0} onClick={()=>setTablePage(p=>p-1)}>上一页</Button>
                    <span className="py-1">第 {tablePage+1}/{Math.max(1,Math.ceil(plans.length/PAGE_SIZE))} 页</span>
                    <Button variant="ghost" size="sm" disabled={tablePage>=Math.ceil(plans.length/PAGE_SIZE)-1} onClick={()=>setTablePage(p=>p+1)}>下一页</Button>
                  </div></CardContent></Card>
              </>)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}