from celery.result import AsyncResult
from fastapi import APIRouter

from app.models.schemas import JobKind, JobRequest, JobStatus
from app.pipeline.tasks import prepare_articles, prepare_citations
from app.worker import celery_app

router = APIRouter(prefix="/jobs", tags=["Belge Hazırlama İşleri"])


@router.post("", response_model=JobStatus)
def create_job(req: JobRequest):
    task = prepare_articles if req.kind == JobKind.ARTICLES else prepare_citations
    result = task.delay(req.model_dump(mode="json"))
    return JobStatus(job_id=result.id, state="PENDING")


@router.get("/{job_id}", response_model=JobStatus)
def job_status(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    info = res.info if isinstance(res.info, dict) else {}
    message = info.get("message") or (str(res.info) if res.failed() else None)
    return JobStatus(
        job_id=job_id,
        state=res.state,
        progress=100 if res.successful() else info.get("progress", 0),
        message=message,
        output_files=info.get("output_files", []) if res.successful() else [],
    )
