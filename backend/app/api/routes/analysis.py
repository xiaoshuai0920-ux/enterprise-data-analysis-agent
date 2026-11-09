import asyncio
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.security import CurrentUser, get_current_user
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import run_analysis

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("", response_model=AnalysisResponse)
async def analyze(payload: AnalysisRequest, current_user: CurrentUser = Depends(get_current_user)):
    return await run_analysis(
        payload.question,
        user_id=current_user.user_id,
        role=current_user.role,
        allowed_regions=current_user.region_scope,
    )

@router.post("/stream")
async def analyze_stream(payload: AnalysisRequest, current_user: CurrentUser = Depends(get_current_user)):
    async def event_generator():
        yield _event("status", {"message": "正在理解问题"})
        await asyncio.sleep(0.05)
        try:
            response = await run_analysis(
                payload.question,
                user_id=current_user.user_id,
                role=current_user.role,
                allowed_regions=current_user.region_scope,
            )
            yield _event("plan", response.plan.model_dump(mode="json"))
            yield _event("data", {"sql": response.sql})
            yield _event("visualization", response.visualization.model_dump(mode="json"))
            yield _event("insight", {"content": response.insight})
            yield _event("done", {"trace_id": response.trace_id, "trace": response.trace})
        except Exception as exc:
            yield _event("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )

def _event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
