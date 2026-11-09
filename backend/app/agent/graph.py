from langgraph.graph import END, START, StateGraph
from app.agent.state import AnalysisState
from app.llm.deepseek import summarize_with_deepseek
from app.services.database import execute_query
from app.services.planner import build_plan_with_llm, normalize_question
from app.services.query_builder import build_query
from app.services.sql_guard import validate_readonly_sql
from app.services.visualization import build_visualization

async def normalize_node(state: AnalysisState) -> dict:
    return {"normalized_question": normalize_question(state["question"])}

async def planner_node(state: AnalysisState) -> dict:
    return {"plan": await build_plan_with_llm(state["normalized_question"])}

async def build_query_node(state: AnalysisState) -> dict:
    query = build_query(state["plan"], state["allowed_regions"])
    validate_readonly_sql(query.sql)
    return {"sql": query.sql, "sql_params": query.params}

async def execute_query_node(state: AnalysisState) -> dict:
    return {"rows": await execute_query(state["sql"], state["sql_params"])}

async def visualization_node(state: AnalysisState) -> dict:
    return {"visualization": build_visualization(state["plan"], state["rows"])}

async def summarize_node(state: AnalysisState) -> dict:
    insight = await summarize_with_deepseek(
        state["question"], state["plan"].model_dump(), state["rows"]
    )
    return {"insight": insight}

builder = StateGraph(AnalysisState)
builder.add_node("normalize", normalize_node)
builder.add_node("planner", planner_node)
builder.add_node("build_query", build_query_node)
builder.add_node("execute_query", execute_query_node)
builder.add_node("visualization", visualization_node)
builder.add_node("summarize", summarize_node)
builder.add_edge(START, "normalize")
builder.add_edge("normalize", "planner")
builder.add_edge("planner", "build_query")
builder.add_edge("build_query", "execute_query")
builder.add_edge("execute_query", "visualization")
builder.add_edge("visualization", "summarize")
builder.add_edge("summarize", END)
analysis_graph = builder.compile()
