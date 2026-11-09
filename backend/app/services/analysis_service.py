import time
from app.agent.graph import analysis_graph
from app.core.trace import TraceCollector
from app.models.schemas import AnalysisResponse
from app.services.cache import get_cache, make_cache_key, set_cache

async def run_analysis(question: str, *, user_id: str, role: str, allowed_regions: list[str]) -> AnalysisResponse:
    trace = TraceCollector()
    cache_key = make_cache_key({
        "question": question.strip().lower(),
        "user_id": user_id,
        "role": role,
        "allowed_regions": sorted(allowed_regions),
    })
    cached = await get_cache(cache_key)
    if cached:
        cached["trace"]["cache_hit"] = True
        return AnalysisResponse.model_validate(cached)

    started = time.perf_counter()
    result = await analysis_graph.ainvoke(
        {
            "question": question,
            "user_id": user_id,
            "role": role,
            "allowed_regions": allowed_regions,
        },
        config={"recursion_limit": 12},
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    trace.add(
        "analysis_graph",
        duration_ms,
        input_summary={"question": question[:120], "allowed_regions": allowed_regions},
        output_summary={"rows": len(result.get("rows", [])), "visualization": result["visualization"].type},
    )

    response = AnalysisResponse(
        trace_id=trace.trace_id,
        question=question,
        plan=result["plan"],
        sql=result["sql"],
        visualization=result["visualization"],
        insight=result["insight"],
        trace=trace.to_dict(),
    )
    await set_cache(cache_key, response.model_dump(mode="json"))
    return response
