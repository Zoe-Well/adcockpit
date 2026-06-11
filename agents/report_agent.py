"""Report Agent — generates structured report from execution results."""
from datetime import datetime
from typing import Dict, Any
from agents.state import AgentState
from tools.mock_data import REPORT_SUMMARY, DASHBOARD_METRICS


def report_agent_node(state: AgentState) -> Dict[str, Any]:
    """Aggregate all upstream outputs into a structured report."""
    scene = state["current_scene"]
    analysis = state.get("analysis_result", {})
    results = state.get("execution_results", [])
    task_graph = list(state["task_graph"])

    # Count results
    success_count = sum(1 for r in results if r.get("status") == "success")
    failed_count = sum(1 for r in results if r.get("status") == "failed")
    cancelled_count = sum(1 for r in results if r.get("status") == "cancelled")

    if scene == "ad_placement":
        report = _ad_placement_report(analysis, results, success_count, failed_count)
    elif scene == "content":
        report = _content_report(results, success_count)
    elif scene == "ecommerce":
        report = _ecommerce_report(analysis, results, success_count)
    elif scene == "data_analysis":
        report = _data_report(analysis, results)
    elif scene == "diagnosis":
        report = _diagnosis_report(analysis, results)
    else:
        report = {"title": "执行报告", "summary": [f"完成 {success_count} / 失败 {failed_count}"]}

    for t in task_graph:
        if t["type"] == "report":
            t["status"] = "done"

    return {"report": report, "task_graph": task_graph}


def _ad_placement_report(analysis, results, success_count, failed_count) -> Dict:
    anomalies = analysis.get("anomalies", [])
    plan_names = [f"{a['plan_id']}({a.get('name','')})" for a in anomalies]

    return {
        "title": "今日投放优化报告",
        "scene": "ad_placement",
        "summary": [
            f"分析计划数: {analysis.get('total_analyzed', 10)} 条（抖音 5 + 腾讯 5）",
            f"不达标计划: {len(anomalies)} 条（ROI < 2.0）",
            f"建议调价: {sum(1 for a in anomalies)} 条计划降价 10%",
            f"建议降预算: {sum(1 for a in anomalies if a['roi'] < 1.5)} 条计划降 20%",
            f"预计节省消耗: ¥{REPORT_SUMMARY['estimated_saving_amount']:,}/天（{REPORT_SUMMARY['estimated_saving']}）",
            f"预计 ROI 提升: {REPORT_SUMMARY['roi_improvement_from']} → {REPORT_SUMMARY['roi_improvement_to']}（+12.3%）",
        ],
        "actions_taken": success_count,
        "actions_failed": failed_count,
        "estimated_saving": REPORT_SUMMARY["estimated_saving"],
        "estimated_saving_amount": REPORT_SUMMARY["estimated_saving_amount"],
        "roi_improvement_from": REPORT_SUMMARY["roi_improvement_from"],
        "roi_improvement_to": REPORT_SUMMARY["roi_improvement_to"],
        "recommendations": [
            "持续监控调价后 ROI 变化，48 小时后评估效果",
            "关注 T001 计划素材审核状态",
            "ROI < 1.5 的计划考虑换素材而非单纯降价",
        ],
        "generated_at": datetime.now().isoformat(),
    }


def _content_report(results, success_count) -> Dict:
    return {
        "title": "内容生产与分发报告",
        "scene": "content",
        "summary": [
            f"生成脚本: 3 条",
            f"发布到飞书: {success_count} 条成功",
        ],
        "generated_at": datetime.now().isoformat(),
    }


def _ecommerce_report(analysis, results, success_count) -> Dict:
    return {
        "title": "直播场控操作报告",
        "scene": "ecommerce",
        "summary": [
            f"库存补充: {success_count} 次",
            f"优惠券创建: 1 张 (10元, 500张)",
            "催单话术: 已推送至中控台",
            "预估 GMV 增量: +¥5,000",
        ],
        "generated_at": datetime.now().isoformat(),
    }


def _data_report(analysis, results) -> Dict:
    ranking = analysis.get("customer_ranking", [])
    return {
        "title": "跨渠道数据分析报告",
        "scene": "data_analysis",
        "summary": [
            f"覆盖客户: {len(ranking)} 个",
            f"回报名 Top3: {', '.join(analysis.get('top3', []))}",
            f"回报率 Bottom2: {', '.join(analysis.get('bottom2', []))}",
            "已生成预算再分配建议和 PPT 提纲",
        ],
        "ppt_outline": analysis.get("ppt_outline", {}),
        "generated_at": datetime.now().isoformat(),
    }


def _diagnosis_report(analysis, results) -> Dict:
    return {
        "title": "故障诊断与恢复报告",
        "scene": "diagnosis",
        "summary": [
            f"根因: {analysis.get('cause_detail', '未知')}",
            f"自动恢复: {'是' if analysis.get('auto_recoverable') else '否（需人工介入）'}",
            f"执行恢复操作: {len(results)} 项",
        ],
        "root_cause": analysis.get("root_cause"),
        "generated_at": datetime.now().isoformat(),
    }
