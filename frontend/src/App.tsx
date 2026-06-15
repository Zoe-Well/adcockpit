import { useState, useEffect, useRef } from 'react'
import { Button } from './components/ui/button'
import { Card, CardHeader, CardContent } from './components/ui/card'
import { Input } from './components/ui/input'
import { Badge } from './components/ui/badge'

type Tab = 'optimize' | 'create' | 'content' | 'ecommerce' | 'data_analysis' | 'diagnosis'
type Message = { role: 'user' | 'agent'; content: string }
const API = 'http://localhost:8000'

const TRACE: Record<string, { flow: string[]; steps: { title: string; desc: string; result: string }[] }> = {
  optimize: {
    flow: ['意图识别','数据拉取','数据拉取','智能分析','策略生成','执行操作','报告生成'],
    steps: [
      {title:'意图识别 — 任务规划',desc:'识别为投放优化意图，拆解为 6 个子任务。抖音和腾讯数据将并行拉取。',result:''},
      {title:'数据拉取 — 抖音',desc:'拉取抖音近7天消耗最高的5条计划，涵盖消耗、ROI、出价等指标。',result:'5条计划 · 拉取完成'},
      {title:'数据拉取 — 腾讯广告',desc:'拉取腾讯广告近7天消耗最高的5条计划，数据已与抖音侧合并。',result:'5条计划 · 拉取完成'},
      {title:'智能分析 — 异常检测',desc:'分析10条计划，筛选ROI低于阈值的异常计划，标注严重程度。',result:'发现3条异常 · 不达标占比37.6%'},
      {title:'策略生成 — 优化方案',desc:'生成4条动作：3条降价10% + 1条降预算20%，预计每天节省¥5,640。',result:'降价+降预算 · 预计改善整体ROI'},
      {title:'执行操作 — 等待确认',desc:'中高风险操作需审批。请查看左侧确认卡片。',result:'等待审批'},
      {title:'报告生成 — 完成',desc:'优化报告已生成，可在右侧仪表盘查看更新数据。',result:'优化完成'},
    ]
  },
  content: {
    flow: ['意图识别','素材拉取','智能分析','脚本生成','执行操作','报告生成'],
    steps: [
      {title:'意图识别 — 任务规划',desc:'识别为内容生产意图，拆解为5个子任务。将基于投放数据优化素材内容。',result:''},
      {title:'素材拉取 — 数据获取',desc:'获取指定平台的高点击率和低点击率素材数据，用于对比分析。',result:'6条素材 · 高CTR 3条 + 低CTR 3条'},
      {title:'智能分析 — 爆款特征',desc:'AI分析高点击视频的共性：前3秒价格锚点、快语速、热门BGM、15-30秒时长。',result:'4个爆款特征 · 低点击素材开场平淡'},
      {title:'脚本生成 — 内容创作',desc:'基于爆款特征和选定模板，生成带货口播脚本。每条脚本包含开场钩子+产品卖点+下单引导。',result:'3条脚本已生成'},
      {title:'执行操作 — 等待确认',desc:'脚本预览已生成，确认后将发布到飞书文档。',result:'等待确认'},
      {title:'报告生成 — 完成',desc:'内容生产流程完成。脚本已可在飞书中查看和编辑。',result:'内容生产完成'},
    ]
  },
  create: {
    flow: ['参数配置','平台审核','执行操作','报告生成'],
    steps: [
      {title:'参数配置 — 接收需求',desc:'已接收投放计划参数：平台、计划名称、日预算、出价、定向信息。',result:''},
      {title:'平台审核 — 提交校验',desc:'提交至广告平台审核：验证预算范围、出价合理性、定向设置。',result:'审核通过'},
      {title:'执行操作 — 等待确认',desc:'计划已通过审核，等待确认上线。',result:'等待确认'},
      {title:'报告生成 — 完成',desc:'计划已创建并上线，初始数据将在投放后回传。',result:'创建成功'},
    ]
  }
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
  const [msgs, setMsgs] = useState<Message[]>([{role:'agent',content:'你好，我是 AdCockpit AI 优化师。我可以帮你完成广告投放优化、内容生产、直播监控、数据分析和故障诊断。\n\n请用自然语言描述你的需求。'}])
  const [input, setInput] = useState('')
  const [showParam, setShowParam] = useState(false)
  const [traceStep, setTraceStep] = useState(-1)
  const [approval, setApproval] = useState(false)
  const [approvalData, setApprovalData] = useState<{id:string;a:string;r:string}[]>([])
  const [bizScene, setBizScene] = useState('ad_placement')
  const [plans, setPlans] = useState(FALLBACK)
  const [contentPlatform, setContentPlatform] = useState('douyin')
  const [contentTemplate, setContentTemplate] = useState('summer_promo')
  const [contentCount, setContentCount] = useState('3')
  const [createForm, setCreateForm] = useState({platform:'douyin',name:'',budget:'5000',bid:'25'})
  const [createdList, setCreatedList] = useState<{name:string;id:string;platform:string;budget:number;bid:number;time:string}[]>([])
  const [agentSteps, setAgentSteps] = useState<{node:string;title:string;status:string;output:string}[]>([])
  const [contentRecords, setContentRecords] = useState<{scripts:string[];urls:string[];platform:string;template:string;time:string}[]>([])
  const [tablePage, setTablePage] = useState(0)
  const PAGE_SIZE = 5
  const msgsRef = useRef<HTMLDivElement>(null)

  useEffect(() => { msgsRef.current?.scrollTo(0, msgsRef.current.scrollHeight) }, [msgs])

  const loadPlans = async () => {
    try {
      const r = await fetch(`${API}/api/campaigns/all`)
      if (r.ok) { const d = await r.json(); if (d.plans?.length) setPlans(d.plans) }
    } catch {}
  }
  useEffect(() => { loadPlans() }, [])

  const sendMsg = async () => {
    const t = input.trim(); if (!t) return
    setMsgs(p => [...p, {role:'user',content:t}]); setInput('')
    try {
      const r = await fetch(`${API}/api/intent/classify`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_input:t,history:msgs.slice(-6)})})
      const d = await r.json()
      if (d.type === 'business') { setBizScene(d.scene||'ad_placement'); if(d.scene==='create'){setTab('create');setMsgs(p=>[...p,{role:'agent',content:d.reply||'请在下方表单填写投放参数。'}]);setShowParam(false)}else{setMsgs(p=>[...p,{role:'agent',content:d.reply||'收到。请调整参数后执行。'}]);setShowParam(true)} }
      else setMsgs(p => [...p,{role:'agent',content:d.reply||'请具体描述你的需求。'}])
    } catch { setMsgs(p => [...p,{role:'agent',content:'后端未连接。先启动: uvicorn backend.app.api.main:app --port 8000'}]) }
  }

  const runOptimize = () => {
    setShowParam(false); setTraceStep(0); setApproval(false); setApprovalData([])
    const sc = TRACE[tab]||TRACE.optimize
    const stopIdx = sc.flow.length - 2
    const total = stopIdx * 3 + 1; let frame = 0
    const iv = setInterval(() => { frame++; setTraceStep(Math.min(Math.floor(frame/3),stopIdx)); if(frame>=total){clearInterval(iv);setApproval(true)} }, 150)
    // Fetch real data for approval card
    fetch(`${API}/api/campaigns/all`).then(r=>r.json()).then(d=>{
      const items:any[]=[]
      const bp=0.9; const budp=0.8
      d.plans?.filter((p:any)=>(p.roi||0)<2.0&&p.roi>0).forEach((p:any)=>{
        items.push({id:p.id,a:`降价至 ¥${(p.bid*bp).toFixed(1)}`,r:p.roi<1.2?'HIGH':p.roi<1.5?'MEDIUM':'LOW'})
        if(p.roi<1.5) items.push({id:p.id,a:`降预算至 ¥${Math.round(p.budget*budp)}`,r:'HIGH'})
      })
      if(items.length>0) setApprovalData(items.slice(0,6))
    })
  }

  const runContent = () => {
    setShowParam(false); setTraceStep(0); setApproval(false)
    const csc = TRACE.content
    const stopIdx = csc.flow.length - 2
    const total = stopIdx * 3 + 1; let frame = 0
    const iv = setInterval(() => { frame++; setTraceStep(Math.min(Math.floor(frame/3),stopIdx)); if(frame>=total){clearInterval(iv);setApproval(true)} }, 150)
  }

  const confirmContent = async () => {
    setApproval(false)
    setMsgs(p => [...p, {role:'agent', content:'正在生成脚本并发布到飞书...'}])
    try {
      const r = await fetch(`${API}/api/content/generate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({platform:contentPlatform,top_n:parseInt(contentCount)||3,template_id:contentTemplate})})
      const d = await r.json()
      // Publish all scripts to one shared Feishu doc
      let feishuMsg = ''
      try {
        const pr = await fetch(`${API}/api/content/publish`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scripts:d.scripts,platform:contentPlatform,template_id:contentTemplate})})
        const pd = await pr.json()
        if (pd.url) feishuMsg = '\n\n📄 飞书文档: '+pd.url
      } catch {}
      setTraceStep(6)
      setContentRecords(prev => [{scripts:d.scripts||[],urls:feishuMsg?[feishuMsg]:[],platform:contentPlatform,template:contentTemplate,time:new Date().toLocaleTimeString()},...prev])
      setMsgs(p => [...p, {role:'agent', content:'已生成 '+d.scripts?.length+' 条脚本！\n'+d.scripts?.map((s:string,i:number)=>`脚本${i+1}: ${s.substring(0,80)}...`).join('\n')+feishuMsg}])
    } catch { setMsgs(p => [...p, {role:'agent', content:'生成失败，请确认后端已启动'}]) }
  }

  const confirmOptimize = async () => {
    setApproval(false)
    setTraceStep(sc.flow.length)
    setMsgs(p => [...p, {role:'agent', content:'正在执行优化...'}])
    try {
      const r = await fetch(`${API}/api/campaigns/optimize`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({platforms:['douyin','tencent'],days:7,top_n:5,roi_threshold:2.0,bid_adjust_pct:-10,budget_adjust_pct:-20})})
      const d = await r.json()
      setMsgs(p => [...p, {role:'agent', content:`优化完成！共调整 ${d.changes?.length||0} 项。\n${d.changes?.slice(0,10).map((c:string)=>'  '+c).join('\n')}`}])
      loadPlans()
    } catch { setMsgs(p => [...p, {role:'agent', content:'优化请求失败'}]) }
  }

  const runCreate = () => {
    if (!createForm.name.trim()) return
    setBizScene('create')
    setShowParam(false); setTraceStep(0); setApproval(false)
    const csc = TRACE.create; const stopIdx = csc.flow.length - 2
    const total = stopIdx * 3 + 1; let frame = 0
    const iv = setInterval(() => { frame++; setTraceStep(Math.min(Math.floor(frame/3),stopIdx)); if(frame>=total){clearInterval(iv);setApproval(true)} }, 150)
  }

  const confirmCreate = async () => {
    setApproval(false); setTraceStep(4)
    setMsgs(p => [...p, {role:'agent', content:'正在创建投放计划...'}])
    try {
      const budgetNum = parseInt(createForm.budget)||5000
      const bidNum = parseFloat(createForm.bid)||25
      const r = await fetch(`${API}/api/campaigns/create`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({platform:createForm.platform,name:createForm.name,budget:budgetNum,bid:bidNum})})
      const d = await r.json()
      loadPlans()
      setCreatedList(prev => [{name:createForm.name,id:d.campaign?.id||'?',platform:createForm.platform,budget:budgetNum,bid:bidNum,time:new Date().toLocaleTimeString()},...prev])
      setMsgs(p => [...p, {role:'agent', content:`投放计划已上线！\n\n${d.campaign?.name} (${d.campaign?.id})\n平台: ${createForm.platform==='douyin'?'抖音':'腾讯广告'}\n日预算: ¥${budgetNum.toLocaleString()}\n出价: ¥${bidNum}`}])
      setCreateForm({platform:'douyin',name:'',budget:'5000',bid:'25'})
    } catch { setMsgs(p => [...p, {role:'agent', content:'创建失败'}]) }
  }

  const tabs: {key:Tab;label:string}[] = [
    {key:'optimize',label:'投放优化'},{key:'create',label:'广告投放'},{key:'content',label:'内容生产'},
    {key:'ecommerce',label:'直播监控'},{key:'data_analysis',label:'数据分析'},{key:'diagnosis',label:'故障诊断'},
  ]

  const traceScene = traceStep >= 0 ? (bizScene === 'content' ? 'content' : bizScene === 'create' ? 'create' : 'optimize') : tab
  const sc = TRACE[traceScene] || TRACE.optimize
  const an = traceStep < 0 ? -1 : traceStep
  const roi = plans.length ? (plans.reduce((s:number,p:any)=>s+(p.roi||0),0)/plans.length).toFixed(2) : '1.87'
  const cost = plans.length ? plans.reduce((s:number,p:any)=>s+(p.cost||0),0).toLocaleString() : '37,600'
  const below = plans.filter((p:any) => (p.roi||0) < 2.0).length

  return (
    <div className="h-screen flex flex-col bg-[#f7f8fc] text-[#1e293b]">
      <header className="h-[52px] bg-white border-b border-slate-200 flex items-center px-6 gap-4 flex-shrink-0 shadow-sm z-20">
        <span className="font-bold text-[16px] text-blue-600 tracking-tight">AdCockpit</span>
        <span className="text-slate-500 text-sm">| AI 数字营销驾驶舱</span>
        <div className="ml-auto flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1"><span className="w-[7px] h-[7px] rounded-full bg-emerald-500"/>系统运行中</span>
          <span>2026-06-14</span><span>会话: demo</span>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <nav className="w-[200px] bg-white border-r border-slate-200 flex flex-col py-5 flex-shrink-0 overflow-y-auto">
          <div className="text-[10px] font-semibold uppercase tracking-[1px] text-slate-400 px-4 pb-2">业务操作</div>
          {tabs.slice(0,3).map(t=>(
            <button key={t.key} onClick={()=>{setTab(t.key);setTraceStep(-1);setApproval(false);setShowParam(false)}}
              className={`flex items-center gap-2 px-4 py-2.5 text-[13px] rounded-md mx-2 mb-0.5 font-medium text-left ${tab===t.key?'bg-blue-50 text-blue-600 font-semibold':'text-slate-500 hover:bg-slate-50'}`}>{t.label}</button>
          ))}
          <div className="border-t border-slate-200 mx-4 my-3"/>
          <div className="text-[10px] font-semibold uppercase tracking-[1px] text-slate-400 px-4 pb-2">数据监控</div>
          {tabs.slice(3).map(t=>(
            <button key={t.key} onClick={()=>{setTab(t.key);setTraceStep(-1);setApproval(false);setShowParam(false)}}
              className={`flex items-center gap-2 px-4 py-2.5 text-[13px] rounded-md mx-2 mb-0.5 font-medium text-left ${tab===t.key?'bg-blue-50 text-blue-600 font-semibold':'text-slate-500 hover:bg-slate-50'}`}>{t.label}</button>
          ))}
          <div className="flex-1"/>
          <div className="border-t border-slate-200 mx-4 mb-3"/>
          <button className="flex items-center gap-2 px-4 py-2 text-[13px] text-slate-500 hover:bg-slate-50 rounded-md mx-2 mb-1">🌐 English / 中文</button>
          <div className="flex items-center gap-2 px-4 py-2 mx-2 mb-2 bg-slate-50 rounded-md">
            <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-semibold">王</div>
            <div><div className="text-[12px] font-semibold">优化师小王</div><div className="text-[9px] text-slate-400">wang@agency.com</div></div>
          </div>
        </nav>

        <div className="flex flex-1 overflow-hidden">
          {/* Chat */}
          <div className="w-[30%] min-w-[360px] flex flex-col border-r border-slate-200">
            <div className="px-4 py-3 bg-white border-b border-slate-200 text-[11px] font-semibold uppercase tracking-[0.5px] text-slate-500 flex-shrink-0">对话面板</div>
            <div className="flex-1 flex flex-col overflow-hidden">
              <div ref={msgsRef} className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 scrollbar">
                {msgs.map((m,i)=>(
                  <div key={i} className={`flex gap-2 ${m.role==='user'?'flex-row-reverse':''}`}>
                    <div className={`w-[30px] h-[30px] rounded-md flex items-center justify-center text-xs font-semibold flex-shrink-0 ${m.role==='agent'?'bg-blue-600 text-white':'bg-slate-100 border border-slate-200 text-slate-500'}`}>{m.role==='agent'?'AI':'王'}</div>
                    <div className={`max-w-[85%] px-3.5 py-2.5 rounded-lg text-[13px] leading-relaxed whitespace-pre-wrap ${m.role==='agent'?'bg-white border border-slate-200':'bg-blue-600 text-white'}`}>{m.content}</div>
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
                        <Button size="sm" variant="outline" className="flex-1 border-red-400 text-red-500" onClick={()=>{setApproval(false);setMsgs(p=>[...p,{role:'agent',content:'操作已取消。'}])}}>取消</Button>
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
                        <Button size="sm" variant="outline" className="flex-1 border-red-400 text-red-500" onClick={()=>{setApproval(false);setMsgs(p=>[...p,{role:'agent',content:'投放已取消。'}])}}>取消</Button>
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
                        <Button size="sm" variant="outline" className="flex-1 border-red-400 text-red-500" onClick={()=>{setApproval(false);setMsgs(p=>[...p,{role:'agent',content:'操作已取消。'}])}}>取消</Button>
                      </div>
                    </CardContent></Card></div>
                )}
              </div>
              {showParam && bizScene === 'ad_placement' && (
                <Card className="mx-4 mb-3"><CardContent className="p-4">
                  <h4 className="text-[13px] font-semibold mb-3">优化参数设置</h4>
                  <div className="grid grid-cols-2 gap-2.5 mb-2.5">
                    {['投放平台','时间范围','拉取计划数','ROI 阈值','出价调整 %','预算调整 %'].map((l,i)=>(<div key={l}><label className="text-[11px] text-slate-500 block mb-1">{l}</label>{i<2?<select className="w-full px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-slate-50"><option>{i===0?'抖音 + 腾讯广告':'近 7 天'}</option></select>:<Input type="number" defaultValue={['5','2.0','-10','-20'][i-2]}/>}</div>))}</div>
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
                  <div className="flex gap-2"><Button size="sm" onClick={runContent}>预览脚本</Button><Button size="sm" variant="outline" onClick={()=>setShowParam(false)}>取消</Button></div>
                </CardContent></Card>
              )}
              <div className="px-4 py-3 bg-white border-t border-slate-200 flex gap-2">
                <Input placeholder="描述你的优化需求..." value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&sendMsg()}/>
                <Button onClick={sendMsg}>发送</Button>
              </div>
            </div>
          </div>

          {/* Trace */}
          <div className="w-[28%] min-w-[360px] flex flex-col border-r border-slate-200">
            <div className="px-4 py-3 bg-white border-b border-slate-200 text-[11px] font-semibold uppercase tracking-[0.5px] text-slate-500 flex-shrink-0">Agent 编排追踪</div>
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2.5 scrollbar">
              <div className="flex items-center justify-center gap-0 py-3">
                {sc.flow.map((label,i)=>(
                  <span key={i} className="flex items-center gap-0">{i>0&&<div className={`w-6 h-[2px] ${i<=an?'bg-emerald-500':'bg-slate-200'}`}/>}
                    <div className="flex flex-col items-center gap-1"><div className={`w-[22px] h-[22px] rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${i<an?'border-emerald-500 bg-emerald-50 text-emerald-600':i===an?'border-blue-500 bg-blue-50 text-blue-600 anim-pulse':'border-slate-200 bg-white text-slate-400'}`}>{i<an?'✓':i===an?'⋯':''}</div><span className="text-[9px] text-slate-400 whitespace-nowrap">{label}</span></div></span>
                ))}
              </div>
              {agentSteps.length>0 && agentSteps.map((step,i)=>(
                <div key={i} className={`rounded-lg border border-slate-200 bg-white p-3 flex gap-2.5 ${step.status==='done'?'border-l-[3px] border-l-emerald-500 opacity-100':'border-l-[3px] border-l-blue-500 opacity-100'}`}>
                  <div className={`w-7 h-7 rounded-md flex items-center justify-center text-[13px] flex-shrink-0 ${step.status==='done'?'bg-emerald-50 text-emerald-600':'bg-blue-50 text-blue-600'}`}>{step.status==='done'?'✓':'⋯'}</div>
                  <div><div className="text-xs font-semibold">{step.title}</div><div className="text-[11px] text-slate-500 leading-relaxed">LLM 输出: {step.output||''}</div></div></div>
              ))}
              {agentSteps.length===0 && an>=0 && sc.steps.map((step,i)=>(
                <div key={i} className={`rounded-lg border border-slate-200 bg-white p-3 flex gap-2.5 ${i<an?'border-l-[3px] border-l-emerald-500 opacity-100':i===an?'border-l-[3px] border-l-blue-500 opacity-100':'opacity-50'}`}>
                  <div className={`w-7 h-7 rounded-md flex items-center justify-center text-[13px] flex-shrink-0 ${i<an?'bg-emerald-50 text-emerald-600':i===an?'bg-blue-50 text-blue-600':'bg-slate-100'}`}>{i<an?'✓':i===an?'⋯':''}</div>
                  <div><div className="text-xs font-semibold">{step.title}</div><div className="text-[11px] text-slate-500 leading-relaxed">{i<an?step.desc:i===an?step.desc.substring(0,Math.floor(step.desc.length*0.6))+'▌':''}</div>{i<an&&step.result&&<div className="mt-1.5 px-2.5 py-1.5 bg-slate-50 rounded text-[11px] text-slate-500">{step.result}</div>}</div></div>
              ))}
              {an<0&&<p className="text-[11px] text-slate-400 text-center mt-4">在对话面板输入需求，系统将在此展示 Agent 编排过程</p>}
            </div>
          </div>

          {/* Dashboard */}
          <div className="w-[42%] min-w-[440px] flex flex-col">
            <div className="px-4 py-3 bg-white border-b border-slate-200 text-[11px] font-semibold uppercase tracking-[0.5px] text-slate-500 flex-shrink-0">数据洞察仪表盘 <span className="font-normal text-slate-400 text-[9px]">{{optimize:'投放优化',create:'广告投放',content:'内容生产',ecommerce:'电商场控',data_analysis:'数据分析',diagnosis:'故障诊断'}[tab]}模式</span></div>
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3.5 scrollbar">
              {tab === 'create' ? (<>
                <div className="grid grid-cols-3 gap-2.5">
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">在投计划</div><div className="text-[22px] font-bold">{plans.length}</div><div className="text-[11px] text-emerald-500 mt-1">抖音+腾讯</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">本次创建</div><div className="text-[22px] font-bold">{createdList.length}</div><div className="text-[11px] text-emerald-500 mt-1">本会话</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">总预算</div><div className="text-[22px] font-bold">{(plans.reduce((s:number,p:any)=>s+(p.budget||0),0)).toLocaleString()}</div><div className="text-[11px] text-emerald-500 mt-1">日预算合计</div></CardContent></Card>
                </div>
                <Card><CardContent className="p-4"><h4 className="text-xs font-semibold text-slate-500 mb-3">平台投放分布</h4>
                  <div className="flex gap-4"><div className="flex-1 text-center"><div className="text-[28px] font-bold text-blue-600">{plans.filter((p:any)=>p._platform==='douyin').length}</div><div className="text-[11px] text-slate-400 mt-1">抖音</div></div><div className="flex-1 text-center"><div className="text-[28px] font-bold text-blue-600">{plans.filter((p:any)=>p._platform==='tencent').length}</div><div className="text-[11px] text-slate-400 mt-1">腾讯</div></div></div></CardContent></Card>
                {createdList.length>0&&<Card><CardHeader><h4 className="text-xs font-semibold text-slate-500">本次创建记录</h4></CardHeader><CardContent className="p-0"><table className="w-full text-[11px]"><thead><tr className="bg-slate-50 text-slate-500 font-medium"><th className="text-left px-3 py-2">时间</th><th className="text-left px-3 py-2">ID</th><th className="text-left px-3 py-2">名称</th><th className="text-left px-3 py-2">平台</th><th className="text-left px-3 py-2">预算</th><th className="text-left px-3 py-2">出价</th></tr></thead><tbody>{createdList.map((c,i)=>(<tr key={i} className="border-b border-slate-100 last:border-b-0"><td className="px-3 py-2">{c.time}</td><td className="px-3 py-2">{c.id}</td><td className="px-3 py-2">{c.name}</td><td className="px-3 py-2">{c.platform==='douyin'?'抖音':'腾讯'}</td><td className="px-3 py-2">¥{c.budget.toLocaleString()}</td><td className="px-3 py-2">¥{c.bid}</td></tr>))}</tbody></table></CardContent></Card>}
                {createdList.length===0&&<p className="text-[11px] text-slate-400 text-center py-8">在左侧填写投放计划并提交，新计划将出现在此处</p>}
              </>) : tab === 'content' ? (<>
                <div className="grid grid-cols-3 gap-2.5">
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">已生成脚本</div><div className="text-[22px] font-bold">{contentRecords.length}</div><div className="text-[11px] text-emerald-500 mt-1">本次会话</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">飞书文档</div><div className="text-[22px] font-bold">{contentRecords.length}</div><div className="text-[11px] text-emerald-500 mt-1">已发布</div></CardContent></Card>
                  <Card><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">使用模板</div><div className="text-[22px] font-bold">{contentRecords.length>0?'夏季促销':'—'}</div><div className="text-[11px] text-emerald-500 mt-1">{contentTemplate==='summer_promo'?'夏季促销':contentTemplate==='flash_sale'?'闪购秒杀':'产品测评'}</div></CardContent></Card>
                </div>
                <Card>
                  <CardHeader><h4 className="text-xs font-semibold text-slate-500">爆款素材特征分析（基于 AI 分析）</h4></CardHeader>
                  <CardContent className="p-4">
                    <div className="grid grid-cols-2 gap-3 text-[11px]">
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500"/> 前3秒出现价格锚点或产品特写</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500"/> 主播语速偏快，制造紧迫感</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500"/> BGM 为当前热门卡点曲目</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500"/> 视频时长控制在 15-30 秒</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-amber-400"/> 低点击视频开场无钩子</div>
                      <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-amber-400"/> 低点击视频语速过慢</div>
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
              </>) : (<>
              <div className="grid grid-cols-3 gap-2.5">
                <Card className="border-red-300 bg-red-50"><CardContent className="p-4"><div className="text-[11px] text-slate-400 uppercase tracking-[0.3px] mb-1.5">整体 ROI</div><div className="text-[22px] font-bold text-red-500">{roi}</div><div className="text-[11px] text-red-400 mt-1">实时数据</div></CardContent></Card>
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
