"""Ortak veri sözleşmesi (tüm öğrenciler bu modelleri kullanır).

Bu dosyada değişiklik yapmak gerekirse Pull Request açılmalı ve 4 öğrencinin de onayı alınmalıdır;
çünkü veri toplama (Öğrenci 1), indeks/kanıt (Öğrenci 2), PDF (Öğrenci 3) ve arayüz/API (Öğrenci 4)
aynı modeller üzerinden haberleşir.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- Yazar
class AuthorCandidate(BaseModel):
    """Google Scholar yazar arama sonucu (aynı isimli birden fazla akademisyen olabilir)."""

    scholar_id: str = Field(..., description="Scholar profil kimliği, ör. 'AbCdEfGhIjk'")
    name: str
    affiliation: str | None = None  # "Burdur Mehmet Akif Ersoy Üniversitesi"
    email_domain: str | None = None  # "mehmetakif.edu.tr" (Scholar'da 'Verified email at ...')
    photo_url: str | None = None
    cited_by_total: int | None = None
    interests: list[str] = []


# --------------------------------------------------------------------------- Yayın türü / indeks
class WorkType(str, Enum):
    JOURNAL_ARTICLE = "journal_article"  # dergi makalesi
    REVIEW = "review"  # derleme (dergi makalesi sayılır)
    PROCEEDINGS = "proceedings"  # bildiri (konferans)
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    THESIS = "thesis"
    PREPRINT = "preprint"
    OTHER = "other"
    UNKNOWN = "unknown"


class IndexType(str, Enum):
    """Kılavuzdaki dizin grupları."""

    SCIE = "SCIE"  # Science Citation Index Expanded (SCI / SCI-EXP)
    SSCI = "SSCI"
    AHCI = "AHCI"
    ESCI = "ESCI"
    SCOPUS = "SCOPUS"
    TR_DIZIN = "TR_DIZIN"  # ULAKBİM TR Dizin
    OTHER_INTERNATIONAL = "OTHER_INTERNATIONAL"  # diğer uluslararası hakemli dizinler
    INTERNATIONAL_BOOK = "INTERNATIONAL_BOOK"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class JournalInfo(BaseModel):
    title: str
    issn: str | None = None
    eissn: str | None = None
    publisher: str | None = None
    homepage_url: str | None = None
    founded_year: int | None = None  # 5 yıl kuralı için
    indexes: list[IndexType] = []
    index_evidence_urls: dict[str, str] = {}  # IndexType -> kanıt sayfası URL'si


# --------------------------------------------------------------------------- Yayın
class Publication(BaseModel):
    """Başvuru sahibinin bir yayını."""

    id: str = Field(..., description="Uygulama içi kimlik (Scholar citation id veya DOI)")
    title: str
    authors: list[str] = []
    year: int | None = Field(None, description="Basılı sayı (issue) yılı - teşvikte esas alınan yıl")
    online_year: int | None = Field(None, description="Erken görünüm (online first) yılı")
    venue: str | None = None
    doi: str | None = None
    work_type: WorkType = WorkType.UNKNOWN
    journal: JournalInfo | None = None
    volume: str | None = None
    issue: str | None = None
    pages: str | None = None
    scholar_url: str | None = None
    cited_by_url: str | None = None
    cited_by_count: int | None = None
    pdf_url: str | None = None  # açık erişim PDF (Unpaywall/OpenAlex)
    openalex_id: str | None = None


class CitingWork(Publication):
    """Başvuru sahibinin bir yayınına atıf yapan çalışma."""

    cited_publication_id: str = Field(..., description="Atıf alan (başvuru sahibine ait) yayın id")


# --------------------------------------------------------------------------- Karar / kanıt planı
class Decision(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MANUAL_CHECK = "manual_check"


class EvidenceKind(str, Enum):
    PDF_FIRST_PAGE = "pdf_first_page"  # makalenin ilk sayfası (tarih + yazar işaretli)
    PDF_REFERENCE_PAGE = "pdf_reference_page"  # atıf veren makalenin kaynakça sayfası (atıf işaretli)
    INDEX_SCREENSHOT = "index_screenshot"  # MJL / TR Dizin / dergi 'Indexing' sayfası
    FOUNDED_YEAR_SCREENSHOT = "founded_year_screenshot"  # derginin 5 yıldır yayın yaptığı kanıt
    EDITORIAL_BOARD_SCREENSHOT = "editorial_board_screenshot"  # yabancı editör/yayın kurulu
    BOOK_PROOF_SCREENSHOT = "book_proof_screenshot"  # uluslararası kitap olduğunu gösteren belge
    DATABASE_CITATION_REPORT = "database_citation_report"  # WoS/Scopus filtreli atıf listesi (kullanıcı yükler)


class EvidenceItem(BaseModel):
    order: int
    kind: EvidenceKind
    label: str = Field(..., description="Belge üzerine kırmızı yazılacak açıklama (kılavuzdaki ifade)")
    highlight_terms: list[str] = []
    source_url: str | None = None
    file_path: str | None = None  # üretildikten sonra doldurulur
    done: bool = False
    note: str | None = None


class EvaluationResult(BaseModel):
    decision: Decision
    reasons: list[str] = []
    index: IndexType = IndexType.UNKNOWN
    evidence_plan: list[EvidenceItem] = []


class PublicationRow(BaseModel):
    """Arayüzde listelenen satır: yayın + değerlendirme."""

    publication: Publication
    evaluation: EvaluationResult


class CitationRow(BaseModel):
    citing: CitingWork
    cited: Publication
    evaluation: EvaluationResult


# --------------------------------------------------------------------------- Yıl
class YearOption(BaseModel):
    data_year: int = Field(..., description="Yayın/atıfların ait olduğu yıl (filtrelenecek yıl)")
    application_year: int = Field(..., description="Teşvik başvurusunun yapılacağı yıl")
    label: str
    recommended: bool = False
    hint: str


# --------------------------------------------------------------------------- İş (job)
class JobKind(str, Enum):
    ARTICLES = "articles"
    CITATIONS = "citations"


class JobRequest(BaseModel):
    kind: JobKind
    scholar_id: str
    author_name: str
    data_year: int
    item_ids: list[str] = Field(default_factory=list, description="Boşsa kabul edilen tüm kalemler")


class JobStatus(BaseModel):
    job_id: str
    state: str  # PENDING | STARTED | PROGRESS | SUCCESS | FAILURE
    progress: int = 0  # 0-100
    message: str | None = None
    output_files: list[str] = []
