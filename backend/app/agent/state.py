from typing import Any, TypedDict
from app.models.schemas import QueryPlan, VisualizationSpec

class AnalysisState(TypedDict, total=False):
    question: str
    user_id: str
    role: str
    allowed_regions: list[str]
    normalized_question: str
    plan: QueryPlan
    sql: str
    sql_params: dict[str, Any]
    rows: list[dict[str, Any]]
    visualization: VisualizationSpec
    insight: str
    error: str | None
