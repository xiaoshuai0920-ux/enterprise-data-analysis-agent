from typing import Any, Literal
from pydantic import BaseModel, Field

ChartType = Literal["bar", "line", "pie", "table", "metric"]

class AnalysisRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None

class MetricCard(BaseModel):
    label: str
    value: float | int | str
    unit: str | None = None
    change: float | None = None

class SeriesSpec(BaseModel):
    name: str
    field: str
    type: Literal["bar", "line"] | None = None

class ColumnSpec(BaseModel):
    title: str
    field: str
    data_type: Literal["string", "number", "percent", "currency"] = "string"

class VisualizationSpec(BaseModel):
    type: ChartType
    title: str
    subtitle: str | None = None
    x_field: str | None = None
    x_label: str | None = None
    series: list[SeriesSpec] = Field(default_factory=list)
    columns: list[ColumnSpec] = Field(default_factory=list)
    data: list[dict[str, Any]] = Field(default_factory=list)
    metrics: list[MetricCard] = Field(default_factory=list)

class QueryPlan(BaseModel):
    metric: str
    dimensions: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    time_range: str
    comparison: str | None = None
    visualization: ChartType = "table"
    limit: int = 50

class AnalysisResponse(BaseModel):
    trace_id: str
    question: str
    plan: QueryPlan
    sql: str
    visualization: VisualizationSpec
    insight: str
    trace: dict[str, Any]
