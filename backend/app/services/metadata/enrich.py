"""Scholar verisini güvenilir metadata ile zenginleştirme (Sorumlu: Öğrenci 1).

Scholar; DOI, ISSN, yayın türü (makale/bildiri), cilt/sayı ve basım yılını güvenilir vermez.
Bu yüzden her kayıt başlık+yıl ile aşağıdaki açık API'lerde eşleştirilir:

  OpenAlex  https://api.openalex.org/works?search=<başlık>&mailto=<CONTACT_EMAIL>
            * type / primary_location.source.type  -> 'journal' | 'conference'  (MAKALE/BİLDİRİ ayrımı)
            * biblio.volume/issue/first_page          -> erken görünüm tespiti
            * primary_location.source.issn            -> indeks sorgusu için ISSN
            * Atıf doğrulama: /works?filter=cites:<W_id>,publication_year:<yıl>
            * best_oa_location.pdf_url                -> PDF indirme
  Crossref  https://api.crossref.org/works/<doi>   (type: journal-article | proceedings-article,
            published-print vs published-online -> basım yılı / erken görünüm yılı)
  Unpaywall https://api.unpaywall.org/v2/<doi>?email=<CONTACT_EMAIL>  -> açık erişim PDF

Başlık eşleştirmesi rapidfuzz.token_set_ratio >= 92 ve |yıl farkı| <= 1 ile yapılmalı.
"""
from app.models.schemas import CitingWork, Publication


def enrich_publication(pub: Publication) -> Publication:
    raise NotImplementedError("TODO(Öğrenci 1)")


def enrich_citing_work(work: CitingWork) -> CitingWork:
    raise NotImplementedError("TODO(Öğrenci 1)")
