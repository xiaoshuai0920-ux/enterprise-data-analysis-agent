from dataclasses import dataclass
from app.models.schemas import QueryPlan
from app.services.semantic_layer import DIMENSION_COLUMNS, get_metric

@dataclass
class BuiltQuery:
    sql: str
    params: dict

def _time_clause(time_range: str, params: dict) -> str:
    if time_range == "2026":
        return "year = 2026"
    if time_range == "2025":
        return "year = 2025"
    if time_range == "2026-09":
        params["month_filter"] = "2026-09"
        return "month = :month_filter"
    if time_range == "2026-08":
        params["month_filter"] = "2026-08"
        return "month = :month_filter"
    if time_range == "last_6_months":
        return "month >= '2026-04' AND month <= '2026-09'"
    return "year = 2026"

def build_query(plan: QueryPlan, allowed_regions: list[str]) -> BuiltQuery:
    metric = get_metric(plan.metric)
    dimensions = [d for d in plan.dimensions if d in metric.allowed_dimensions]
    select_parts = [DIMENSION_COLUMNS[d] for d in dimensions]
    select_parts.append(f"{metric.expression} AS value")

    params: dict = {}
    where = [_time_clause(plan.time_range, params)]

    allowed_placeholders = []
    for index, region in enumerate(allowed_regions):
        key = f"allowed_region_{index}"
        params[key] = region
        allowed_placeholders.append(f":{key}")
    where.append(f"region IN ({', '.join(allowed_placeholders)})" if allowed_placeholders else "1 = 0")

    if region := plan.filters.get("region"):
        params["region_filter"] = region
        where.append("region = :region_filter")
    if product := plan.filters.get("product"):
        params["product_filter"] = product
        where.append("product = :product_filter")

    group_by = ""
    order_by = " ORDER BY value DESC"
    if dimensions:
        group_by = " GROUP BY " + ", ".join(DIMENSION_COLUMNS[d] for d in dimensions)
        if dimensions == ["month"]:
            order_by = " ORDER BY month ASC"

    sql = (
        "SELECT " + ", ".join(select_parts)
        + " FROM sales_metrics WHERE " + " AND ".join(where)
        + group_by + order_by + f" LIMIT {min(plan.limit, 100)}"
    )
    return BuiltQuery(sql=sql, params=params)
