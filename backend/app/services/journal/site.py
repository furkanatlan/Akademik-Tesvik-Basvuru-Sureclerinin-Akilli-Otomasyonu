"""Dergi web sitesi kanıtları — "diğer uluslararası" dergiler için (Sorumlu: Öğrenci 3).

Kılavuz s.6-7, s.26-27, s.30-31:
  * "5 senedir yayınlandığını gösteren kanıt (arşivde eklenebilir)"  -> founded_year + yaş >= 5
  * "tarandığı dizinler"                                              -> Indexing / Abstracting / Dizinler sayfası
  * "editör/yayın kurulunun yabancı olduğunu gösteren kısım"          -> Editorial Board sayfasındaki yabancı üyeler
  * "uluslararası kitap olduğunu gösteren belge"                      -> yayınevi sayfası (ISBN)

Sayfa bulma: ana sayfadaki bağlantı metinleri (TR/EN) ile; DergiPark için sabit yollar:
  https://dergipark.org.tr/tr/pub/<dergi>/indexes | /board | /archive
Ekran görüntüleri app.services.evidence.screenshot.capture ile, kılavuz etiketleriyle alınır.
"""
from app.models.schemas import JournalInfo

LINK_KEYWORDS = {
    "indexing": ["indexing", "indexed", "abstracting", "index", "dizin", "taranan"],
    "editorial_board": ["editorial board", "editorial team", "yayın kurulu", "editörler", "board"],
    "archive": ["archive", "arşiv", "all issues", "back issues"],
    "about": ["about", "hakkında", "aims and scope", "amaç ve kapsam"],
}


def find_journal_pages(homepage_url: str) -> dict[str, str]:
    """{'indexing': url, 'editorial_board': url, 'archive': url, 'about': url}"""
    raise NotImplementedError("TODO(Öğrenci 3)")


def founded_year(journal: JournalInfo) -> int | None:
    """'Founded/Since/Başlangıç' ifadesinden veya arşivdeki ilk cilt yılından kuruluş yılı."""
    raise NotImplementedError("TODO(Öğrenci 3)")


def foreign_board_members(editorial_board_url: str) -> list[str]:
    """Yayın kurulunda Türkiye dışındaki üye satırları (işaretlenecek metinler)."""
    raise NotImplementedError("TODO(Öğrenci 3)")
