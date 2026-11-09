from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.analysis import router as analysis_router
from app.api.routes.meta import router as meta_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analysis_router)
app.include_router(meta_router)

@app.get("/health")
async def health():
    return {"status": "ok", "mock_mode": settings.mock_mode, "model": settings.deepseek_model}
