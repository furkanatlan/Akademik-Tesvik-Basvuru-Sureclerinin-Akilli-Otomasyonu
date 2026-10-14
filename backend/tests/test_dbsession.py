from app.services.dbsession.scopus import citing_query, query_url


def test_scopus_citing_query_applies_guide_filters():
    q = citing_query("2-s2.0-84962630852", 2026, "55931223000")
    assert "REFEID(2-s2.0-84962630852)" in q
    assert "PUBYEAR IS 2026" in q  # yıl sınırlaması (s.13 m.3)
    assert "PUBSTAGE(final)" in q  # Article in Press hariç (s.13 m.1)
    assert "NOT AU-ID(55931223000)" in q  # kendine atıf hariç (s.13 m.2)
    assert "DOCTYPE(ar OR re)" in q  # bildiri içindeki atıflar hariç


def test_scopus_query_url_is_encoded():
    assert query_url("DOI(10.1/x)").startswith("https://www.scopus.com/results/results.uri?")
