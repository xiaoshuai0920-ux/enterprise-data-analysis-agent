from typing import Any
from app.models.schemas import ColumnSpec, MetricCard, QueryPlan, SeriesSpec, VisualizationSpec
from app.services.semantic_layer import get_metric

DIMENSION_LABELS = {"region": "区域", "product": "产品", "month": "月份"}

def _value_type(metric_code: str) -> str:
    if metric_code in {"sales_amount", "gross_profit"}:
        return "currency"
    if metric_code == "gross_margin":
        return "percent"
    return "number"

def build_visualization(plan: QueryPlan, rows: list[dict[str, Any]]) -> VisualizationSpec:
    metric = get_metric(plan.metric)
    title = f"{metric.name}分析"
    normalized_rows: list[dict[str, Any]] = []

    for row in rows:
        item = dict(row)
        raw_value = float(item.get("value") or 0)
        if plan.metric == "gross_margin":
            item["value"] = round(raw_value * 100, 2)
        else:
            item["value"] = round(raw_value, 2)
        normalized_rows.append(item)

    if plan.visualization == "table":
        columns = [
            ColumnSpec(title=DIMENSION_LABELS.get(dim, dim), field=dim, data_type="string")
            for dim in plan.dimensions
        ]
        columns.append(ColumnSpec(title=metric.name, field="value", data_type=_value_type(plan.metric)))
        return VisualizationSpec(type="table", title=title, columns=columns, data=normalized_rows)

    if not plan.dimensions:
        value = normalized_rows[0]["value"] if normalized_rows else 0
        return VisualizationSpec(
            type="metric", title=title,
            metrics=[MetricCard(label=metric.name, value=value, unit=metric.unit)]
        )

    x_field = plan.dimensions[0]
    if plan.visualization == "pie":
        return VisualizationSpec(
            type="pie", title=title, x_field=x_field,
            x_label=DIMENSION_LABELS.get(x_field, x_field),
            series=[SeriesSpec(name=metric.name, field="value")],
            data=normalized_rows,
        )

    return VisualizationSpec(
        type=plan.visualization, title=title, x_field=x_field,
        x_label=DIMENSION_LABELS.get(x_field, x_field),
        series=[SeriesSpec(name=metric.name, field="value", type=plan.visualization)],
        data=normalized_rows,
    )
