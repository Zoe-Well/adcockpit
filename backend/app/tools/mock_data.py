"""Mock data constants for AdCockpit — MUST match adcockpit-prototype.html exactly."""

DOUYIN_PLANS = [
    {"id": "C001", "name": "夏季促销-A", "cost": 15200, "roi": 1.5, "bid": 25.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.035, "cvr": 0.038, "cpa": 40.0},
    {"id": "C002", "name": "新品首发-B", "cost": 14100, "roi": 2.3, "bid": 30.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.042, "cvr": 0.045, "cpa": 35.0},
    {"id": "C003", "name": "爆款返场-C", "cost": 12800, "roi": 3.1, "bid": 22.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.051, "cvr": 0.052, "cpa": 28.0},
    {"id": "C004", "name": "品牌日-D",   "cost": 9600,  "roi": 1.8, "bid": 20.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.033, "cvr": 0.036, "cpa": 42.0},
    {"id": "C005", "name": "直播引流-E", "cost": 8800,  "roi": 2.5, "bid": 18.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.040, "cvr": 0.043, "cpa": 32.0},
]

TENCENT_PLANS = [
    {"id": "T001", "name": "618大促",   "cost": 12800, "roi": 1.2, "bid": 30.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.028, "cvr": 0.031, "cpa": 45.0},
    {"id": "T002", "name": "会员日",    "cost": 11000, "roi": 2.8, "bid": 28.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.045, "cvr": 0.048, "cpa": 30.0},
    {"id": "T003", "name": "达人种草",  "cost": 9500,  "roi": 3.5, "bid": 24.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.055, "cvr": 0.058, "cpa": 25.0},
    {"id": "T004", "name": "品宣视频",  "cost": 8200,  "roi": 2.1, "bid": 21.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.038, "cvr": 0.040, "cpa": 36.0},
    {"id": "T005", "name": "直播切片",  "cost": 7600,  "roi": 2.6, "bid": 19.0, "budget": 5000, "status": "active", "review_status": "approved", "ctr": 0.043, "cvr": 0.046, "cpa": 33.0},
]

CREATIVES = [
    # High CTR
    {"id": "V001", "platform": "douyin", "name": "夏季促销口播-A", "type": "video", "url": "https://mock.cdn/videos/v001.mp4", "ctr": 0.068, "completion_rate": 0.82, "created_at": "2026-06-08"},
    {"id": "V002", "platform": "douyin", "name": "爆款返场混剪-B", "type": "video", "url": "https://mock.cdn/videos/v002.mp4", "ctr": 0.055, "completion_rate": 0.78, "created_at": "2026-06-08"},
    {"id": "V003", "platform": "douyin", "name": "新品首发开箱-C", "type": "video", "url": "https://mock.cdn/videos/v003.mp4", "ctr": 0.049, "completion_rate": 0.75, "created_at": "2026-06-08"},
    # Low CTR
    {"id": "V004", "platform": "douyin", "name": "品牌宣传片-D", "type": "video", "url": "https://mock.cdn/videos/v004.mp4", "ctr": 0.018, "completion_rate": 0.35, "created_at": "2026-06-08"},
    {"id": "V005", "platform": "douyin", "name": "静态图文-E", "type": "image", "url": "https://mock.cdn/images/i005.jpg", "ctr": 0.012, "completion_rate": 0.30, "created_at": "2026-06-08"},
    {"id": "V006", "platform": "douyin", "name": "长视频讲解-F", "type": "video", "url": "https://mock.cdn/videos/v006.mp4", "ctr": 0.015, "completion_rate": 0.22, "created_at": "2026-06-08"},
]

PRODUCTS = [
    {"id": "A", "name": "爆款T恤", "stock": 32, "reserved": 10, "price": 99.0, "status": "low_stock"},
    {"id": "B", "name": "新品连衣裙", "stock": 200, "reserved": 0, "price": 199.0, "status": "on_sale"},
]

LIVE_METRICS = {
    "room_id": "ROOM-001",
    "online": 2000,
    "gmv": 85000.0,
    "conversion_rate": 0.03,
}

CLIENT_DATA = [
    {
        "name": "客户A",
        "platforms": {
            "douyin": {"cost": 25000, "roi": 1.5, "cpa": 40},
            "tencent": {"cost": 15000, "roi": 1.3, "cpa": 45},
            "xiaohongshu": {"cost": 10000, "roi": 1.8, "cpa": 35},
        }
    },
    {
        "name": "客户B",
        "platforms": {
            "douyin": {"cost": 20000, "roi": 2.2, "cpa": 32},
            "tencent": {"cost": 18000, "roi": 2.5, "cpa": 28},
            "xiaohongshu": {"cost": 12000, "roi": 2.0, "cpa": 38},
        }
    },
    {
        "name": "客户C",
        "platforms": {
            "douyin": {"cost": 18000, "roi": 3.2, "cpa": 22},
            "tencent": {"cost": 12000, "roi": 2.9, "cpa": 25},
            "xiaohongshu": {"cost": 8000, "roi": 3.5, "cpa": 20},
        }
    },
    {
        "name": "客户D",
        "platforms": {
            "douyin": {"cost": 30000, "roi": 1.1, "cpa": 55},
            "tencent": {"cost": 22000, "roi": 1.4, "cpa": 48},
            "xiaohongshu": {"cost": 15000, "roi": 1.2, "cpa": 52},
        }
    },
    {
        "name": "客户E",
        "platforms": {
            "douyin": {"cost": 15000, "roi": 2.8, "cpa": 26},
            "tencent": {"cost": 10000, "roi": 3.0, "cpa": 24},
            "xiaohongshu": {"cost": 6000, "roi": 2.6, "cpa": 30},
        }
    },
]

# Overall dashboard metrics (matches prototype)
DASHBOARD_METRICS = {
    "overall_roi": 1.87,
    "total_cost": 37600,
    "avg_cpa": 38.5,
    "active_plans": 10,
    "avg_ctr": 0.038,
    "avg_cvr": 0.042,
    "anomaly_count": 3,
}

# Report summary (matches prototype)
REPORT_SUMMARY = {
    "estimated_saving": "15%",
    "estimated_saving_amount": 5640,
    "roi_improvement_from": 1.87,
    "roi_improvement_to": 2.1,
}
