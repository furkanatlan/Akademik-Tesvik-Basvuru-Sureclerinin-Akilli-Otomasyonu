from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import routes_authors, routes_dbsession, routes_jobs, routes_years
from app.config import get_settings
from app.services.dbsession.browser import DbLoginRequired
from app.services.dbsession.common import GuidedStepRequired

app = FastAPI(
    title="Akademik Teşvik Otomasyonu API",
    description="Google Scholar'dan yayın/atıf toplayıp MAKÜ kılavuzuna uygun kanıt dosyaları üretir.",
    version="0.1.0",
)

app.include_router(routes_years.router, prefix="/api")
app.include_router(routes_dbsession.router, prefix="/api")
app.include_router(routes_authors.router, prefix="/api")
app.include_router(routes_jobs.router, prefix="/api")


@app.exception_handler(DbLoginRequired)
def _db_login_required(_: Request, exc: DbLoginRequired):
    return JSONResponse(status_code=409, content={"detail": str(exc), "code": "db_login_required"})


@app.exception_handler(GuidedStepRequired)
def _guided_step(_: Request, exc: GuidedStepRequired):
    return JSONResponse(
        status_code=409,
        content={"detail": "Bu adımı tarayıcıda sizin tamamlamanız gerekiyor.", "code": "guided_step",
                 "database": exc.database, "instructions": exc.instructions, "url": exc.url},
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "scholar_provider": get_settings().scholar_provider}
