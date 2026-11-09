from dataclasses import dataclass

@dataclass(frozen=True)
class MetricDefinition:
    code: str
    name: str
    expression: str
    unit: str
    allowed_dimensions: tuple[str, ...]

METRICS: dict[str, MetricDefinition] = {
    "sales_amount": MetricDefinition("sales_amount", "销售额", "SUM(sales_amount)", "元", ("month", "region", "product")),
    "gross_profit": MetricDefinition("gross_profit", "毛利额", "SUM(gross_profit)", "元", ("month", "region", "product")),
    "gross_margin": MetricDefinition(
        "gross_margin", "毛利率",
        "CASE WHEN SUM(sales_amount)=0 THEN 0 ELSE SUM(gross_profit)*1.0/SUM(sales_amount) END",
        "%", ("month", "region", "product")
    ),
    "order_count": MetricDefinition("order_count", "订单数", "SUM(order_count)", "单", ("month", "region", "product")),
}

DIMENSION_COLUMNS = {"month": "month", "region": "region", "product": "product"}

def get_metric(code: str) -> MetricDefinition:
    if code not in METRICS:
        raise ValueError(f"不支持的指标: {code}")
    return METRICS[code]
