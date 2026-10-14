"""Uçtan uca iş akışları (Sorumlu: Öğrenci 4 - diğer modülleri birleştirir).

ÖN KOŞUL (her iki iş): WoS veya Scopus girişi doğrulanmış olmalı
  -> services.dbsession.browser.require_login()  (mock modda atlanır)
  Oturumlu adımlar services.dbsession.browser.shared_context() ile kullanıcının giriş yaptığı tarayıcıda çalışır.
  Otomatik yapılamayan adımda GuidedStepRequired yakalanır; kayıt "kullanıcı tamamlamalı" olarak işaretlenir,
  talimatlar arayüzde gösterilir, kullanıcı ekranı POST /api/db-session/{db}/capture ile kanıt olarak kaydeder.

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
  3. kabul edilenler için evidence_plan uygulanır, atıf başına tek PDF
  4. Yol B (kılavuz s.9-13): atıf alan HER yayın için core.rules.database_citation_plan
       WoS girişi varsa    -> dbsession.wos.citing_report    (Early Access, bildiri, kendine atıf hariç; dizin + yıl)
       Scopus girişi varsa -> dbsession.scopus.citing_report (PUBYEAR, PUBSTAGE(final), NOT AU-ID, DOCTYPE(ar OR re))
     + yayının ilk sayfası -> tek PDF
  5. Tümü ZIP
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
