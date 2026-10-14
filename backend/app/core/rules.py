"""MAKÜ Akademik Teşvik Başvuru Sistemi Kılavuzu (Ocak/2024) kurallarının kod karşılığı.

Her yayın / atıf için:
  1) kabul mü, ret mi, manuel kontrol mü?  (evaluate_*)
  2) kabul ise hangi belgeler, hangi sırayla, hangi işaretlemelerle hazırlanacak? (evidence plan)

Etiket metinleri (label) kılavuzdaki kırmızı açıklamalarla birebir aynıdır; PDF üzerine bu metinler yazılır.
Kılavuz sayfa referansları parantez içinde verilmiştir (ör. s.4).
"""
from app.core.names import same_person
from app.models.schemas import (
    CitingWork,
    Decision,
    EvaluationResult,
    EvidenceItem,
    EvidenceKind,
    IndexType,
    Publication,
    WorkType,
)

WOS_INDEXES = {IndexType.SCIE, IndexType.SSCI, IndexType.AHCI, IndexType.ESCI}
WOS_INDEX_LABELS = {
    IndexType.SCIE: "Science Citation Index Expanded",
    IndexType.SSCI: "Social Sciences Citation Index",
    IndexType.AHCI: "Arts & Humanities Citation Index",
    IndexType.ESCI: "Emerging Sources Citation Index",
}
# Öncelik sırası: bir dergi birden fazla dizinde ise en yüksek puanlı olan kanıtlanır
INDEX_PRIORITY = [
    IndexType.SCIE,
    IndexType.SSCI,
    IndexType.AHCI,
    IndexType.ESCI,
    IndexType.SCOPUS,
    IndexType.OTHER_INTERNATIONAL,
    IndexType.TR_DIZIN,
]
JOURNAL_TYPES = {WorkType.JOURNAL_ARTICLE, WorkType.REVIEW}
MIN_JOURNAL_AGE_YEARS = 5  # "5 senedir yayınlandığını gösteren kanıt" (s.7, s.27)


def primary_index(indexes: list[IndexType]) -> IndexType:
    for idx in INDEX_PRIORITY:
        if idx in indexes:
            return idx
    return IndexType.UNKNOWN if not indexes else indexes[0]


def is_published_in_issue(work: Publication) -> bool:
    """Erken görünüm (Early Access / Article in Press) değil, sayıya girmiş mi? (s.10-13)

    Cilt/sayı ya da sayfa/makale numarası varsa yayımlanmış kabul edilir.
    """
    return bool(work.volume and (work.issue or work.pages))


# =========================================================================== MAKALE
def evaluate_publication(pub: Publication, data_year: int) -> EvaluationResult:
    reasons: list[str] = []
    if pub.year != data_year:
        return EvaluationResult(
            decision=Decision.REJECTED,
            reasons=[f"Yayın yılı {pub.year}, seçilen değerlendirme yılı {data_year}."],
        )
    if pub.work_type not in JOURNAL_TYPES:
        return EvaluationResult(
            decision=Decision.MANUAL_CHECK,
            reasons=[f"Yayın türü '{pub.work_type.value}': bu modül yalnızca dergi makalelerini hazırlar."],
        )
    if pub.online_year and pub.online_year != pub.year:
        reasons.append(
            f"Erken görünüm {pub.online_year}, basım {pub.year}: basım (sayı) yılı esas alındı."
        )
    if not is_published_in_issue(pub):
        return EvaluationResult(
            decision=Decision.MANUAL_CHECK,
            reasons=reasons + ["Cilt/sayı bilgisi yok: erken görünümde olabilir, kontrol edin."],
        )

    indexes = pub.journal.indexes if pub.journal else []
    index = primary_index(indexes)
    if index in (IndexType.UNKNOWN, IndexType.NONE):
        return EvaluationResult(
            decision=Decision.MANUAL_CHECK,
            reasons=reasons + ["Derginin tarandığı dizin otomatik tespit edilemedi."],
            index=index,
        )
    return EvaluationResult(
        decision=Decision.ACCEPTED,
        reasons=reasons,
        index=index,
        evidence_plan=article_evidence_plan(pub, index),
    )


def article_evidence_plan(pub: Publication, index: IndexType) -> list[EvidenceItem]:
    """Makale ekleme (kılavuz s.3-7). Tek PDF'te bu sırayla birleştirilir."""
    journal = pub.journal
    year = str(pub.year) if pub.year else ""
    plan = [
        EvidenceItem(
            order=1,
            kind=EvidenceKind.PDF_FIRST_PAGE,
            label="1.sayfa - tarihin işaretlenmesi / ilgili yazarın işaretlenmesi",
            highlight_terms=[year],  # + yazar adı varyantları (pipeline ekler)
            source_url=pub.pdf_url,
        )
    ]
    if index in WOS_INDEXES:
        plan += [
            EvidenceItem(
                order=2,
                kind=EvidenceKind.INDEX_SCREENSHOT,
                label=f"{index.value} indeksi gösteren belge 2.sayfa - indeksin işaretlenmesi",
                highlight_terms=[WOS_INDEX_LABELS[index]],
                source_url="https://mjl.clarivate.com/search-results",
            ),
            EvidenceItem(
                order=3,
                kind=EvidenceKind.EDITORIAL_BOARD_SCREENSHOT,
                label="Editorial board",
                highlight_terms=["Editorial board", "Editorial Board"],
                source_url=journal.homepage_url if journal else None,
            ),
        ]
    elif index == IndexType.TR_DIZIN:
        plan.append(
            EvidenceItem(
                order=2,
                kind=EvidenceKind.INDEX_SCREENSHOT,
                label="TR Dizin'de tarandığını gösteren belge",
                highlight_terms=["TR Dizin", year],
                source_url="https://search.trdizin.gov.tr/tr/dergi/ara",
            )
        )
    else:  # SCOPUS / diğer uluslararası (s.6-7)
        plan += [
            EvidenceItem(
                order=2,
                kind=EvidenceKind.FOUNDED_YEAR_SCREENSHOT,
                label="5 senedir yayınlandığını gösteren kanıt (arşivde eklenebilir)",
                highlight_terms=["Founded", "Since", "Kuruluş", "Başlangıç"],
                source_url=journal.homepage_url if journal else None,
            ),
            EvidenceItem(
                order=3,
                kind=EvidenceKind.INDEX_SCREENSHOT,
                label="tarandığı dizinler",
                highlight_terms=["Index", "Indexing", "Abstracting", "Dizin"],
                source_url=journal.homepage_url if journal else None,
            ),
            EvidenceItem(
                order=4,
                kind=EvidenceKind.EDITORIAL_BOARD_SCREENSHOT,
                label="editör/yayın kurulunun yabancı olduğunu gösteren kısım",
                highlight_terms=[],  # yabancı ülke/üniversite adları (Öğrenci 2 tespit eder)
                source_url=journal.homepage_url if journal else None,
            ),
        ]
    return plan


# =========================================================================== ATIF
def evaluate_citation(
    citing: CitingWork, cited: Publication, applicant_name: str, data_year: int
) -> EvaluationResult:
    """Atıf kabul kuralları (kılavuz s.10-31 + proje kuralı).

    BİLDİRİ KURALI — belirleyici olan atıfı YAPAN çalışmanın türüdür:
      * Hocanın herhangi bir yayınına (makale VEYA bildiri) bir BİLDİRİ içinde yapılan atıf  -> RET
      * Hocanın BİLDİRİSİNE bir dergi MAKALESİ içinde yapılan atıf                          -> KABUL
    Atıf ALAN yayının türü (cited.work_type) kararı etkilemez.
    """
    if citing.year != data_year:
        return EvaluationResult(
            decision=Decision.REJECTED,
            reasons=[f"Atıf yapan çalışmanın yılı {citing.year}, değerlendirme yılı {data_year}."],
        )
    if any(same_person(applicant_name, a) for a in citing.authors):
        return EvaluationResult(
            decision=Decision.REJECTED,
            reasons=["Kendine atıf: başvuru sahibi atıf yapan çalışmanın yazarları arasında (s.10, s.13)."],
        )
    if citing.work_type == WorkType.PROCEEDINGS:
        return EvaluationResult(
            decision=Decision.REJECTED,
            reasons=["Atıfı yapan çalışma bir bildiri (konferans/kongre/sempozyum): "
                     "bildiri içinde yapılan atıflar kabul edilmez."],
        )
    if citing.work_type in (WorkType.THESIS, WorkType.PREPRINT, WorkType.OTHER):
        return EvaluationResult(
            decision=Decision.REJECTED,
            reasons=[f"Atıf yapan çalışma türü '{citing.work_type.value}': dergi makalesi değil."],
        )
    if citing.work_type in (WorkType.BOOK, WorkType.BOOK_CHAPTER):
        return EvaluationResult(
            decision=Decision.MANUAL_CHECK,
            reasons=["Kitap/kitap bölümünde atıf: uluslararası kitap olduğu doğrulanmalı (s.21-23)."],
            index=IndexType.INTERNATIONAL_BOOK,
            evidence_plan=book_citation_plan(citing, cited),
        )
    if citing.work_type == WorkType.UNKNOWN:
        return EvaluationResult(
            decision=Decision.MANUAL_CHECK,
            reasons=["Atıf yapan çalışmanın türü (makale/bildiri) belirlenemedi."],
        )
    if not is_published_in_issue(citing):
        return EvaluationResult(
            decision=Decision.REJECTED,
            reasons=["Erken görünüm (Early Access / Article in Press): henüz sayıya girmemiş (s.10, s.13)."],
        )

    index = primary_index(citing.journal.indexes if citing.journal else [])
    if index in (IndexType.UNKNOWN, IndexType.NONE):
        return EvaluationResult(
            decision=Decision.MANUAL_CHECK,
            reasons=["Atıf yapan derginin dizini tespit edilemedi."],
            index=index,
        )
    notes = []
    if cited.work_type == WorkType.PROCEEDINGS:
        notes.append("Atıf alan yayınınız bir bildiri; atıf bir dergi makalesinden geldiği için kabul edilir.")
    return EvaluationResult(
        decision=Decision.ACCEPTED,
        reasons=notes,
        index=index,
        evidence_plan=citation_evidence_plan(citing, cited, index),
    )


def citation_evidence_plan(citing: CitingWork, cited: Publication, index: IndexType) -> list[EvidenceItem]:
    """'Atıfların doğrudan atıf yapan makaleler üzerinden gösterilmesi' (s.14-31)."""
    journal = citing.journal
    plan = [
        EvidenceItem(
            order=1,
            kind=EvidenceKind.PDF_REFERENCE_PAGE,
            label="atıf veren makalenin kaynakça kısmında atıf verilen makalenin işaretlenmesi",
            highlight_terms=[cited.title],
            source_url=citing.pdf_url,
        ),
        EvidenceItem(
            order=2,
            kind=EvidenceKind.PDF_FIRST_PAGE,
            label="atıf veren makalenin ilk sayfası",
            highlight_terms=[],
            source_url=citing.pdf_url,
        ),
    ]
    if index in WOS_INDEXES:
        plan.append(
            EvidenceItem(
                order=3,
                kind=EvidenceKind.INDEX_SCREENSHOT,
                label=f"atıf veren makalenin {index.value} olduğunu gösteren belge (highlighted)",
                highlight_terms=[WOS_INDEX_LABELS[index]],
                source_url="https://mjl.clarivate.com/search-results",
            )
        )
    elif index == IndexType.TR_DIZIN:
        plan.append(
            EvidenceItem(
                order=3,
                kind=EvidenceKind.INDEX_SCREENSHOT,
                label="atıf veren TRdizin derginin indeksini gösteren belge",
                highlight_terms=["TR Dizin", str(citing.year or "")],
                source_url="https://search.trdizin.gov.tr/tr/dergi/ara",
            )
        )
    else:  # SCOPUS / diğer uluslararası hakemli dergi (s.24-31)
        plan += [
            EvidenceItem(
                order=3,
                kind=EvidenceKind.INDEX_SCREENSHOT,
                label="atıf veren makalenin uluslararası index olduğunu gösteren belge",
                highlight_terms=["Index", "Indexing", "Scopus"],
                source_url=journal.homepage_url if journal else None,
            ),
            EvidenceItem(
                order=4,
                kind=EvidenceKind.FOUNDED_YEAR_SCREENSHOT,
                label="diğer uluslararası hakemli derginin 5 yıldır yayın yaptığını gösteren belge "
                "ve editör, yayın kurulu (arşivde eklenebilir)",
                highlight_terms=["Editorial Board"],
                source_url=journal.homepage_url if journal else None,
            ),
        ]
    return plan


def book_citation_plan(citing: CitingWork, cited: Publication) -> list[EvidenceItem]:
    """Uluslararası basılan kitaptan atıf örneği (s.21-23)."""
    return [
        EvidenceItem(
            order=1,
            kind=EvidenceKind.PDF_REFERENCE_PAGE,
            label="uluslararası basılan kitaptan atıf örneği - işaretleme",
            highlight_terms=[cited.title],
            source_url=citing.pdf_url,
        ),
        EvidenceItem(
            order=2,
            kind=EvidenceKind.PDF_FIRST_PAGE,
            label="atıf verilen uluslararası kitap bölümünün ilk sayfası",
            source_url=citing.pdf_url,
        ),
        EvidenceItem(
            order=3,
            kind=EvidenceKind.BOOK_PROOF_SCREENSHOT,
            label="uluslararası kitap olduğunu gösteren belge",
            highlight_terms=["ISBN"],
            source_url=citing.scholar_url,
        ),
    ]


def database_citation_plan(cited: Publication, database: str, data_year: int, index: IndexType) -> list[EvidenceItem]:
    """Yol B: 'Web of Science ve Scopus veri tabanlarından atıfların gösterilmesi' (s.9-13).

    WoS / Scopus girişi yapıldıktan sonra, atıf alan HER yayın için tek PDF:
      1) başvuru sahibinin atıf alan çalışmasının ilk sayfası
      2) filtrelenmiş atıf listesi ekran görüntüsü (URL damgalı)
    """
    first_page = EvidenceItem(
        order=1,
        kind=EvidenceKind.PDF_FIRST_PAGE,
        label="başvuru sahibinin atıf alan çalışmasının ilk sayfası",
        source_url=cited.pdf_url,
    )
    if database == "wos":
        index_name = WOS_INDEX_LABELS.get(index, WOS_INDEX_LABELS[IndexType.SCIE])
        report = EvidenceItem(
            order=2,
            kind=EvidenceKind.DATABASE_CITATION_REPORT,
            label=f"Web of Science atıf listesi - {index_name}, {data_year} "
            "(Early Access, bildiri ve kendine atıflar hariç)",
            highlight_terms=["Refined By", f"Publication Years: {data_year}", "NOT Document Types: Early Access",
                             "NOT Researcher Profiles", index_name],
            source_url="https://www.webofscience.com/wos/woscc/advanced-search",
        )
    else:
        report = EvidenceItem(
            order=2,
            kind=EvidenceKind.DATABASE_CITATION_REPORT,
            label=f"Scopus atıf listesi - {data_year} (Article in Press, bildiri ve kendine atıflar hariç)",
            highlight_terms=[f"PUBYEAR IS {data_year}", "PUBSTAGE(final)", "NOT AU-ID"],
            source_url="https://www.scopus.com/search/form.uri?display=advanced",
            note="Scopus listesindeki atıfların WoS veya başka dizindeki dergilerde olduğu ayrıca belgelenir (s.13 m.5).",
        )
    return [first_page, report]


def database_citation_checklist(database: str, data_year: int, author_surname: str) -> list[str]:
    """Alternatif yol: WoS / Scopus veri tabanı üzerinden atıf gösterimi (s.10-13).

    Yönlendirmeli (elle tamamlanan) ekran görüntülerinde bu ifadelerin göründüğü OCR ile kontrol edilir.
    """
    if database == "wos":
        return [
            "NOT Document Types: Early Access",  # Proceedings Paper dışlaması listede bildiri varsa görünür
            f"NOT Researcher Profiles: {author_surname}",
            "Web of Science Index:",
            f"Publication Years: {data_year}",
            "webofscience.com",  # URL belge üzerinde görünmeli
        ]
    # Otomatik sorgu (PUBYEAR IS / PUBSTAGE(final) / NOT AU-ID) ya da elle filtre (LIMIT-TO / EXCLUDE)
    return [
        f"PUBYEAR IS {data_year}|LIMIT-TO ( PUBYEAR , {data_year} )",
        "NOT AU-ID|EXCLUDE",
        "scopus.com",
    ]
