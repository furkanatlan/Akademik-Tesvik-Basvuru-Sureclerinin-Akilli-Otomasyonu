"""PDF üzerinde metin bulma, sarı işaretleme ve kırmızı açıklama yazma (Sorumlu: Öğrenci 3).

Temel fonksiyonlar hazırdır. Öğrenci 3'ün ekleyeceği zor kısımlar:
  * find_reference_entry(): kaynakça bölümünde atıf alan yayının satırını bulmak
    (satır sonu tirelemesi, farklı atıf stilleri [APA/IEEE/Vancouver], numaralı kaynakça)
  * OCR fallback: metin katmanı olmayan PDF'lerde ocrmypdf ile metin katmanı eklemek
"""
from pathlib import Path

import pymupdf

YELLOW = (1.0, 0.83, 0.0)
RED = (0.86, 0.0, 0.0)
FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def highlight_on_page(page: pymupdf.Page, terms: list[str]) -> int:
    """Sayfada terimleri bulur ve highlight annotation ekler. Bulunan alan sayısını döndürür."""
    found = 0
    for term in terms:
        if not term:
            continue
        for quad in page.search_for(term, quads=True):
            annot = page.add_highlight_annot(quad)
            annot.set_colors(stroke=YELLOW)
            annot.update()
            found += 1
    return found


def add_label(page: pymupdf.Page, text: str, y: float = 18) -> None:
    """Sayfanın üstüne kılavuzdaki gibi kırmızı açıklama yazar (Türkçe karakter destekli)."""
    rect = pymupdf.Rect(36, y - 14, page.rect.width - 36, y + 20)
    page.insert_textbox(
        rect,
        text,
        fontsize=12,
        fontname="dejavu",
        fontfile=FONT_FILE,
        color=RED,
        align=pymupdf.TEXT_ALIGN_CENTER,
    )


def extract_pages(src: Path, page_numbers: list[int], dst: Path) -> Path:
    """Sadece ilgili sayfaları yeni PDF'e kopyalar (kılavuz: 'belgelerin sadece ilgili bölümleri')."""
    with pymupdf.open(src) as doc, pymupdf.open() as out:
        for n in page_numbers:
            out.insert_pdf(doc, from_page=n, to_page=n)
        out.save(dst, garbage=4, deflate=True)
    return dst


def find_reference_entry(doc: pymupdf.Document, cited_title: str) -> tuple[int, list] | None:
    """Kaynakçada atıf alan yayının geçtiği (sayfa_no, [Rect...]) bilgisini döndürür."""
    raise NotImplementedError("TODO(Öğrenci 3)")
