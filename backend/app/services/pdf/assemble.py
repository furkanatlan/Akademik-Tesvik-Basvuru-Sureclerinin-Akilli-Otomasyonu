"""Kanıt parçalarını tek PDF'te birleştirme (Sorumlu: Öğrenci 3).

Her makale / her atıf için TEK dosya üretilir. Sıra rules.py'deki evidence_plan 'order' alanıdır.
Dosya adı önerisi:
  /data/output/<scholar_id>/<yıl>/makaleler/01_<ilk-yazar>_<kısa-başlık>.pdf
  /data/output/<scholar_id>/<yıl>/atiflar/<atıf-alan-yayın-kısa>/01_<atıf-yapan-kısa>.pdf
Sonunda tümü bir ZIP'e konur ve arayüzden indirilir.
"""
from pathlib import Path

import img2pdf
import pymupdf


def png_to_pdf(png: Path, dst: Path) -> Path:
    dst.write_bytes(img2pdf.convert(str(png)))
    return dst


def merge_pdfs(parts: list[Path], dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with pymupdf.open() as out:
        for part in parts:
            with pymupdf.open(part) as doc:
                out.insert_pdf(doc)
        out.save(dst, garbage=4, deflate=True)
    return dst
