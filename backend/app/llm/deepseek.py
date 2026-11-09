import json
import httpx
from app.core.config import settings

SYSTEM_PROMPT = """
你是企业数据分析 Agent 的分析总结节点。
你只能基于给定的查询计划与真实数据做总结，不允许创造不存在的数字。
请用简洁中文输出：
1. 一句话结论；
2. 最重要的 2~3 个数据事实；
3. 如果数据不足，明确说明。
"""

async def summarize_with_deepseek(question: str, plan: dict, rows: list[dict]) -> str:
    if settings.mock_mode or not settings.deepseek_api_key:
        return mock_summary(question, plan, rows)

    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(
                {"question": question, "plan": plan, "data": rows},
                ensure_ascii=False, default=str
            )},
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.deepseek_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

def mock_summary(question: str, plan: dict, rows: list[dict]) -> str:
    if not rows:
        return "当前权限范围与筛选条件下没有查询到可用于分析的数据。"

    ordered = sorted(rows, key=lambda item: float(item.get("value") or 0), reverse=True)
    top = ordered[0]
    dim = next((key for key in ["region", "product", "month"] if key in top), "维度")

    if dim == "month":
        first = rows[0]
        last = rows[-1]
        delta = float(last.get("value") or 0) - float(first.get("value") or 0)
        direction = "上升" if delta >= 0 else "下降"
        return (
            f"当前数据呈现{direction}趋势。区间起点为 {first.get('month')}，指标值 {first.get('value')}；"
            f"区间终点为 {last.get('month')}，指标值 {last.get('value')}。"
            "建议结合活动、渠道和重点客户变化继续做归因下钻。"
        )

    top_name = top.get(dim, "-")
    top_value = float(top.get("value") or 0)
    total = sum(float(row.get("value") or 0) for row in rows)
    share = top_value / total * 100 if total else 0
    return (
        f"从当前查询结果看，{top_name}贡献最高，指标值为 {top_value:.2f}，"
        f"约占当前结果总量的 {share:.1f}%。"
        "如果需要进一步定位原因，可以继续按产品、区域或月份下钻。"
    )
