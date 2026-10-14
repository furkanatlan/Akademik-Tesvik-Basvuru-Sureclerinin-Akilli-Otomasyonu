"""Uçtan uca iş akışları (Sorumlu: Öğrenci 4 - diğer modülleri birleştirir).

prepare_articles:
  1. provider.list_publications(scholar_id) -> yıl filtresi (core.years.is_in_data_year)
  2. metadata.enrich_publication              (Öğrenci 1)
  3. index.resolve_indexes                     (Öğrenci 2)
  4. core.rules.evaluate_publication           -> evidence_plan
  5. her EvidenceItem için: PDF indir + işaretle (Öğrenci 3) / ekran görüntüsü (Öğrenci 2)
  6. pdf.assemble.merge_pdfs -> makale başına tek PDF, sonra ZIP

prepare_citations:
  1. TÜM yayınlar (yıl filtresi YOK) -> her biri için provider.list_citing_works(pub, data_year)
  2. enrich_citing_work -> resolve_indexes -> core.rules.evaluate_citation
     (bildiri, kendine atıf, erken görünüm, yıl dışı -> ELENİR)
  3. kabul edilenler için evidence_plan uygulanır, atıf başına tek PDF, sonra ZIP
"""
from app.models.schemas import JobRequest
from app.worker import celery_app


@celery_app.task(bind=True, name="prepare_articles")
def prepare_articles(self, request: dict) -> dict:
    req = JobRequest(**request)
    self.update_state(state="PROGRESS", meta={"progress": 0, "message": "Başlatıldı"})
    raise NotImplementedError(f"TODO(Öğrenci 4): {req.kind.value} işi")


@celery_app.task(bind=True, name="prepare_citations")
def prepare_citations(self, request: dict) -> dict:
    req = JobRequest(**request)
    self.update_state(state="PROGRESS", meta={"progress": 0, "message": "Başlatıldı"})
    raise NotImplementedError(f"TODO(Öğrenci 4): {req.kind.value} işi")
