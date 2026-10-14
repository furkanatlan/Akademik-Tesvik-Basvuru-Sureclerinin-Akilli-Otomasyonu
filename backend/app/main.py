from fastapi import FastAPI

from app.api import routes_authors, routes_jobs, routes_years
from app.config import get_settings

app = FastAPI(
    title="Akademik Teşvik Otomasyonu API",
    description="Google Scholar'dan yayın/atıf toplayıp MAKÜ kılavuzuna uygun kanıt dosyaları üretir.",
    version="0.1.0",
)

app.include_router(routes_years.router, prefix="/api")
app.include_router(routes_authors.router, prefix="/api")
app.include_router(routes_jobs.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "scholar_provider": get_settings().scholar_provider}
