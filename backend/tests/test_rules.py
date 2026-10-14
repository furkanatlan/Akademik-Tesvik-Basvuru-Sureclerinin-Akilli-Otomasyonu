from datetime import date

from app.core.names import same_person
from app.core.rules import database_citation_plan, evaluate_citation, evaluate_publication
from app.core.years import year_options
from app.models.schemas import CitingWork, Decision, IndexType, JournalInfo, Publication, WorkType

SCIE = JournalInfo(title="J", indexes=[IndexType.SCIE])


def _pub(**kw) -> Publication:
    base = dict(id="p", title="T", year=2026, work_type=WorkType.JOURNAL_ARTICLE, journal=SCIE,
                volume="1", issue="2", pages="1-10", authors=["Ahmet Yılmaz"])
    return Publication(**(base | kw))


def _cit(**kw) -> CitingWork:
    base = dict(id="c", title="C", year=2026, work_type=WorkType.JOURNAL_ARTICLE, journal=SCIE,
                volume="1", issue="2", pages="1-10", authors=["John Smith"], cited_publication_id="p")
    return CitingWork(**(base | kw))


def test_year_options_in_application_season():
    opts = year_options(date(2027, 1, 15))
    assert [(o.data_year, o.application_year) for o in opts] == [(2026, 2027), (2027, 2028)]
    assert opts[0].recommended


def test_year_options_december_prepares_current_year():
    opts = year_options(date(2026, 12, 10))
    rec = next(o for o in opts if o.recommended)
    assert rec.data_year == 2026 and rec.application_year == 2027


def test_publication_accepted_with_three_part_plan():
    r = evaluate_publication(_pub(), 2026)
    assert r.decision == Decision.ACCEPTED
    assert [e.order for e in r.evidence_plan] == [1, 2, 3]


def test_publication_wrong_year_rejected():
    assert evaluate_publication(_pub(year=2025), 2026).decision == Decision.REJECTED


def test_citation_in_proceedings_rejected():
    r = evaluate_citation(_cit(work_type=WorkType.PROCEEDINGS), _pub(), "Ahmet Yılmaz", 2026)
    assert r.decision == Decision.REJECTED


def test_proceedings_citing_applicants_proceedings_rejected():
    """Hocanın bildirisine bir bildiri içinde yapılan atıf da reddedilir."""
    cited = _pub(work_type=WorkType.PROCEEDINGS, year=2019)
    r = evaluate_citation(_cit(work_type=WorkType.PROCEEDINGS), cited, "Ahmet Yılmaz", 2026)
    assert r.decision == Decision.REJECTED


def test_article_citing_applicants_proceedings_accepted():
    """Hocanın BİLDİRİSİNE bir dergi MAKALESİNDE yapılan atıf kabul edilir."""
    cited = _pub(work_type=WorkType.PROCEEDINGS, year=2019, journal=None, volume=None, issue=None, pages=None)
    r = evaluate_citation(_cit(), cited, "Ahmet Yılmaz", 2026)
    assert r.decision == Decision.ACCEPTED
    assert any("bildiri" in reason for reason in r.reasons)


def test_database_plan_has_first_page_and_report():
    plan = database_citation_plan(_pub(), "scopus", 2026, IndexType.SCOPUS)
    assert [e.kind.value for e in plan] == ["pdf_first_page", "database_citation_report"]
    assert "PUBYEAR IS 2026" in plan[1].highlight_terms


def test_self_citation_rejected():
    r = evaluate_citation(_cit(authors=["Yilmaz, A."]), _pub(), "Ahmet Yılmaz", 2026)
    assert r.decision == Decision.REJECTED


def test_early_access_citation_rejected():
    r = evaluate_citation(_cit(volume=None, issue=None, pages=None), _pub(), "Ahmet Yılmaz", 2026)
    assert r.decision == Decision.REJECTED


def test_old_publication_cited_this_year_accepted():
    r = evaluate_citation(_cit(), _pub(year=2015), "Ahmet Yılmaz", 2026)
    assert r.decision == Decision.ACCEPTED


def test_same_person_variants():
    assert same_person("Oğuz Gürsoy", "Gursoy, O.")
    assert same_person("Oğuz Gürsoy", "Gursoy O")
    assert not same_person("Oğuz Gürsoy", "Ali Gürsoy")
