from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.core.rules import evaluate_citation, evaluate_publication
from app.core.years import is_in_data_year
from app.models.schemas import AuthorCandidate, CitationRow, PublicationRow
from app.services.scholar.base import get_provider

router = APIRouter(prefix="/authors", tags=["Yazar / Yayın / Atıf"])


def _enrich_enabled() -> bool:
    # Mock verisi zaten zenginleştirilmiş gelir; gerçek sağlayıcılarda OpenAlex/Crossref/indeks adımı çalışır.
    return get_settings().scholar_provider != "mock"


@router.get("/search", response_model=list[AuthorCandidate])
def search_authors(name: str = Query(..., min_length=3, description="Ad Soyad")):
    return get_provider().search_authors(name.strip())


@router.get("/{scholar_id}/publications", response_model=list[PublicationRow])
def publications(scholar_id: str, year: int):
    """Seçilen yılda YAYIMLANMIŞ makaleler (basım yılı esas)."""
    pubs = [p for p in get_provider().list_publications(scholar_id) if is_in_data_year(p.year, year)]
    if _enrich_enabled():
        from app.services.index.resolver import resolve_indexes
        from app.services.metadata.enrich import enrich_publication

        pubs = [enrich_publication(p) for p in pubs]
        for p in pubs:
            if p.journal:
                p.journal = resolve_indexes(p.journal)
    return [PublicationRow(publication=p, evaluation=evaluate_publication(p, year)) for p in pubs]


@router.get("/{scholar_id}/citations", response_model=list[CitationRow])
def citations(scholar_id: str, year: int, author_name: str):
    """Yazarın TÜM yayınlarına (eski yayınlar dahil) seçilen YILDA yapılan atıflar."""
    provider = get_provider()
    pubs = provider.list_publications(scholar_id)
    if not pubs:
        raise HTTPException(404, "Yazara ait yayın bulunamadı")
    rows: list[CitationRow] = []
    for pub in pubs:
        for citing in provider.list_citing_works(pub, year):
            if _enrich_enabled():
                from app.services.index.resolver import resolve_indexes
                from app.services.metadata.enrich import enrich_citing_work

                citing = enrich_citing_work(citing)
                if citing.journal:
                    citing.journal = resolve_indexes(citing.journal)
            rows.append(
                CitationRow(
                    citing=citing,
                    cited=pub,
                    evaluation=evaluate_citation(citing, pub, author_name, year),
                )
            )
    return rows
