import re
from app.models.schemas import QueryPlan

REGIONS = ["华东", "华南", "华北", "西部"]
PRODUCTS = ["企业版", "专业版", "基础版", "增值服务"]

def normalize_question(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip())

def _metric(question: str) -> str:
    if "毛利率" in question:
        return "gross_margin"
    if "毛利" in question or "利润" in question:
        return "gross_profit"
    if "订单" in question and "销售" not in question:
        return "order_count"
    return "sales_amount"

def _dimensions(question: str) -> list[str]:
    dims: list[str] = []
    has_region_filter = any(region in question for region in REGIONS)
    is_root_cause = any(word in question for word in ["为什么", "原因", "下降", "下滑"])

    if is_root_cause and has_region_filter:
        return ["product"]

    if any(word in question for word in ["区域", "地区", "各区"]):
        dims.append("region")
    if any(word in question for word in ["产品", "版本"]):
        dims.append("product")
    if any(word in question for word in ["趋势", "月份", "每月", "月度", "最近"]):
        dims.append("month")
    if not dims:
        dims.append("region")
    return dims[:2]

def _filters(question: str) -> dict:
    filters: dict[str, str] = {}
    for region in REGIONS:
        if region in question:
            filters["region"] = region
            break
    for product in PRODUCTS:
        if product in question:
            filters["product"] = product
            break
    return filters

def _time_range(question: str) -> str:
    if "今年" in question:
        return "2026"
    if "去年" in question:
        return "2025"
    if "最近6个月" in question or "近6个月" in question:
        return "last_6_months"
    if "本月" in question or "这个月" in question:
        return "2026-09"
    if "上月" in question or "上个月" in question:
        return "2026-08"
    return "2026"

def _visualization(question: str, dimensions: list[str]) -> str:
    if "表格" in question or "table" in question.lower() or "列表" in question:
        return "table"
    if "饼图" in question or "占比" in question:
        return "pie"
    if "折线" in question or "趋势" in question:
        return "line"
    if "柱状" in question or "柱形" in question:
        return "bar"
    if dimensions == ["month"]:
        return "line"
    return "bar"

def build_plan(question: str) -> QueryPlan:
    question = normalize_question(question)
    dimensions = _dimensions(question)
    return QueryPlan(
        metric=_metric(question),
        dimensions=dimensions,
        filters=_filters(question),
        time_range=_time_range(question),
        comparison="mom" if any(x in question for x in ["环比", "下降", "上月"]) else None,
        visualization=_visualization(question, dimensions),
        limit=50,
    )


async def build_plan_with_llm(question: str) -> QueryPlan:
    """真实模型模式使用 DeepSeek 解析 QueryPlan；失败时降级到确定性 Parser。"""
    from app.core.config import settings

    if settings.mock_mode or not settings.deepseek_api_key:
        return build_plan(question)

    import json
    import httpx

    prompt = """
你是企业 BI Data Agent 的 Query Planner。
只输出 JSON，不要输出解释文字。
可用 metric:
- sales_amount
- gross_profit
- gross_margin
- order_count

可用 dimensions:
- region
- product
- month

可用 visualization:
- bar
- line
- pie
- table
- metric

time_range 只允许:
- 2026
- 2025
- 2026-09
- 2026-08
- last_6_months

输出格式:
{
  "metric": "sales_amount",
  "dimensions": ["region"],
  "filters": {},
  "time_range": "2026",
  "comparison": null,
  "visualization": "bar",
  "limit": 50
}

原则：
1. 用户明确说柱状图/折线图/饼图/表格时必须遵循。
2. “趋势”优先 line；“占比”优先 pie；“明细/表格”用 table。
3. 用户提到华东/华南/华北/西部时写入 filters.region。
4. 用户提到企业版/专业版/基础版/增值服务时写入 filters.product。
5. 不要生成 SQL。
"""

    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 400,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.deepseek_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return QueryPlan.model_validate(json.loads(content))
    except Exception:
        return build_plan(question)
