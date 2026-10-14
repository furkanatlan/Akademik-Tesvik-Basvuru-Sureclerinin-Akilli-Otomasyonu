from dataclasses import dataclass, field
from pathlib import Path


class GuidedStepRequired(RuntimeError):
    """Otomatik adım tamamlanamadı; kullanıcı gömülü tarayıcıda adımı elle tamamlamalı.

    Arayüz bu durumda tarayıcıyı ve `instructions` listesini gösterir; kullanıcı işi bitirince
    'Bu ekranı kanıt olarak kaydet' der (POST /api/db-session/{db}/capture).
    """

    def __init__(self, database: str, instructions: list[str], url: str | None = None):
        super().__init__("; ".join(instructions))
        self.database = database
        self.instructions = instructions
        self.url = url


@dataclass
class CitationReport:
    database: str  # wos | scopus
    png_path: Path
    url: str
    result_count: int | None
    applied_filters: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
