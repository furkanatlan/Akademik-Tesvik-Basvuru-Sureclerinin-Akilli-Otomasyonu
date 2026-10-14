import json
from pathlib import Path

from app.models.schemas import AuthorCandidate, CitingWork, Publication
from app.services.scholar.base import ScholarProvider

_DATA = json.loads((Path(__file__).parents[2] / "fixtures" / "mock_data.json").read_text("utf-8"))


class MockProvider(ScholarProvider):
    def search_authors(self, name: str) -> list[AuthorCandidate]:
        q = name.casefold().split()
        return [
            AuthorCandidate(**a)
            for a in _DATA["authors"]
            if all(part in a["name"].casefold() for part in q)
        ]

    def list_publications(self, scholar_id: str) -> list[Publication]:
        return [Publication(**p) for p in _DATA["publications"].get(scholar_id, [])]

    def list_citing_works(self, publication: Publication, year: int) -> list[CitingWork]:
        return [
            CitingWork(**c)
            for c in _DATA["citations"]
            if c["cited_publication_id"] == publication.id and c["year"] == year
        ]
