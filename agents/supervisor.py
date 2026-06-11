"""Supervisor Agent — task decomposition and scene routing."""
from datetime import datetime
from typing import Dict, Any
from agents.state import AgentState, TaskNode


def _is_conversational(user_input: str) -> bool:
    """Check if the input is a general conversation, not a business request."""
    conv_keywords = [
        # Greetings & small talk
        "你好", "嗨", "hello", "hi", "hey", "早上好", "下午好", "晚上好",
        "谢谢", "感谢", "再见", "拜拜", "你是谁", "你是什么", "你叫什么",
        "你能做什么", "你可以做什么", "你会什么", "你的功能", "功能介绍",
        "介绍一下", "帮助", "help", "怎么用", "如何使用",
        # Self/identity questions
        "你是", "你的名字", "你是什么系统", "你是什么模型",
        "你是ai", "你是人工", "谁开发的", "谁做的",
        # Capability questions
        "有什么能力", "能干嘛", "能做什么", "能帮我",
        # Non-business random chat
        "天气", "笑话", "讲个故事", "今天几号", "现在几点",
        "吃饭", "睡觉", "无聊", "随便聊聊",
    ]
    user_lower = user_input.lower()
    return any(kw in user_lower for kw in conv_keywords)


def _is_business_request(user_input: str) -> bool:
    """Check if input contains clear business intent keywords."""
    business_keywords = [
        "roi", "调价", "计划", "消耗", "投放", "广告", "优化",
        "素材", "脚本", "视频", "内容", "混剪", "ctr",
        "直播", "库存", "优惠券", "场控", "补货", "催单",
        "报表", "分析", "预算", "客户", "ppt", "排名", "数据",
        "排查", "诊断", "故障", "没量", "恢复",
        "检查", "拉取", "查询", "生成", "帮我看看", "帮我查",
    ]
    user_lower = user_input.lower()
    return any(kw in user_lower for kw in business_keywords)


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Parse user input, identify scene, and decompose into task graph."""
    user_input = state["user_input"]
    user_lower = user_input.lower()

    # 1. First check if purely conversational
    if _is_conversational(user_input) and not _is_business_request(user_input):
        return {
            "current_scene": "conversational",
            "task_graph": [],
            "conversation_history": state.get("conversation_history", []) + [
                {"role": "user", "content": user_input, "time": datetime.now().isoformat()}
            ],
        }

    # 2. Check for business intent
    if not _is_business_request(user_input):
        # Unclear — ask for clarification instead of defaulting to ad_placement
        return {
            "current_scene": "unclear",
            "task_graph": [],
            "conversation_history": state.get("conversation_history", []) + [
                {"role": "user", "content": user_input, "time": datetime.now().isoformat()}
            ],
        }

    # 3. Business request — identify scene
    if any(kw in user_lower for kw in ["roi", "调价", "计划", "消耗", "投放", "广告", "优化"]):
        current_scene = "ad_placement"
    elif any(kw in user_lower for kw in ["素材", "脚本", "视频", "内容", "混剪", "ctr"]):
        current_scene = "content"
    elif any(kw in user_lower for kw in ["直播", "库存", "优惠券", "场控", "补货", "催单"]):
        current_scene = "ecommerce"
    elif any(kw in user_lower for kw in ["报表", "预算", "客户", "ppt", "排名", "数据", "汇总"]):
        current_scene = "data_analysis"
    elif any(kw in user_lower for kw in ["排查", "诊断", "故障", "没量", "恢复"]):
        current_scene = "diagnosis"
    else:
        current_scene = "ad_placement"

    # Build task graph per scene
    if current_scene == "ad_placement":
        task_graph = _build_ad_placement_tasks()
    elif current_scene == "content":
        task_graph = _build_content_tasks()
    elif current_scene == "ecommerce":
        task_graph = _build_ecommerce_tasks()
    elif current_scene == "data_analysis":
        task_graph = _build_data_analysis_tasks()
    elif current_scene == "diagnosis":
        task_graph = _build_diagnosis_tasks()
    else:
        task_graph = _build_ad_placement_tasks()

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append({"role": "user", "content": state["user_input"], "time": datetime.now().isoformat()})

    return {
        "current_scene": current_scene,
        "task_graph": task_graph,
        "conversation_history": history,
    }


def _build_ad_placement_tasks():
    """Build task graph for ad placement optimization (US1)."""
    return [
        TaskNode(id="T1", type="fetch_data", platform="douyin",
                 params={"metric": "cost", "top_n": 5, "days": 7},
                 depends_on=[], status="pending"),
        TaskNode(id="T2", type="fetch_data", platform="tencent",
                 params={"metric": "cost", "top_n": 5, "days": 7},
                 depends_on=[], status="pending"),
        TaskNode(id="T3", type="analyze",
                 params={"filter": "roi < 2"},
                 depends_on=["T1", "T2"], status="pending"),
        TaskNode(id="T4", type="strategize",
                 depends_on=["T3"], status="pending"),
        TaskNode(id="T5", type="execute",
                 params={"requires_approval": True},
                 depends_on=["T4"], status="pending"),
        TaskNode(id="T6", type="report",
                 depends_on=["T5"], status="pending"),
    ]


def _build_content_tasks():
    return [
        TaskNode(id="T1", type="fetch_data", platform="douyin",
                 params={"endpoint": "get_top_creatives", "metric": "ctr", "top_n": 3, "worst_n": 3},
                 depends_on=[], status="pending"),
        TaskNode(id="T2", type="analyze",
                 params={"analysis_type": "creative_insights"},
                 depends_on=["T1"], status="pending"),
        TaskNode(id="T3", type="strategize",
                 params={"output": "scripts"},
                 depends_on=["T2"], status="pending"),
        TaskNode(id="T4", type="execute",
                 params={"action": "publish_to_feishu", "requires_approval": False},
                 depends_on=["T3"], status="pending"),
        TaskNode(id="T5", type="report",
                 depends_on=["T4"], status="pending"),
    ]


def _build_ecommerce_tasks():
    return [
        TaskNode(id="T1", type="fetch_data", platform=None,
                 params={"endpoint": "get_product_stock,get_live_metrics"},
                 depends_on=[], status="pending"),
        TaskNode(id="T2", type="analyze",
                 params={"analysis_type": "stock_gap"},
                 depends_on=["T1"], status="pending"),
        TaskNode(id="T3", type="strategize",
                 params={"output": "ecommerce_actions"},
                 depends_on=["T2"], status="pending"),
        TaskNode(id="T4", type="execute",
                 params={"requires_approval": True},
                 depends_on=["T3"], status="pending"),
        TaskNode(id="T5", type="report",
                 depends_on=["T4"], status="pending"),
    ]


def _build_data_analysis_tasks():
    return [
        TaskNode(id="T1", type="fetch_data", platform="douyin",
                 params={"endpoint": "get_platform_report"},
                 depends_on=[], status="pending"),
        TaskNode(id="T2", type="fetch_data", platform="tencent",
                 params={"endpoint": "get_platform_report"},
                 depends_on=[], status="pending"),
        TaskNode(id="T3", type="fetch_data", platform="xiaohongshu",
                 params={"endpoint": "get_platform_report"},
                 depends_on=[], status="pending"),
        TaskNode(id="T4", type="analyze",
                 params={"group_by": "client", "metrics": ["cost", "roi", "cpa"]},
                 depends_on=["T1", "T2", "T3"], status="pending"),
        TaskNode(id="T5", type="strategize",
                 params={"output": "budget_proposal"},
                 depends_on=["T4"], status="pending"),
        TaskNode(id="T6", type="report",
                 params={"output": "ppt_outline"},
                 depends_on=["T5"], status="pending"),
    ]


def _build_diagnosis_tasks():
    return [
        TaskNode(id="T1", type="fetch_data", platform="douyin",
                 params={"endpoint": "get_plan_status"},
                 depends_on=[], status="pending"),
        TaskNode(id="T2", type="analyze",
                 params={"analysis_type": "root_cause"},
                 depends_on=["T1"], status="pending"),
        TaskNode(id="T3", type="strategize",
                 params={"output": "recovery_actions"},
                 depends_on=["T2"], status="pending"),
        TaskNode(id="T4", type="execute",
                 params={"requires_approval": False},
                 depends_on=["T3"], status="pending"),
        TaskNode(id="T5", type="report",
                 depends_on=["T4"], status="pending"),
    ]
