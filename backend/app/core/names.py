"""Yazar adı normalizasyonu ve eşleştirme (kendine atıf tespiti, PDF'de yazar arama)."""
import re

from rapidfuzz import fuzz
from unidecode import unidecode


def normalize_name(name: str) -> str:
    """'Oğuz GÜRSOY' -> 'oguz gursoy'"""
    s = unidecode(name).lower()
    s = re.sub(r"[^a-z\s\-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def name_variants(full_name: str) -> list[str]:
    """PDF'de aranacak yazar adı biçimleri: 'Oğuz Gürsoy', 'Gürsoy O', 'O. Gürsoy', 'Gürsoy, O.' ..."""
    parts = full_name.split()
    if len(parts) < 2:
        return [full_name]
    first, last = " ".join(parts[:-1]), parts[-1]
    initials = "".join(p[0] for p in parts[:-1])
    dotted = ". ".join(p[0] for p in parts[:-1]) + "."
    variants = {
        full_name,
        f"{last}, {first}",
        f"{last} {initials}",
        f"{last}, {dotted}",
        f"{dotted} {last}",
        f"{last} {first}",
        last,
    }
    return sorted(variants, key=len, reverse=True)


def _first_last_order(name: str) -> str:
    """'Gürsoy, O.' -> 'O. Gürsoy'"""
    if "," in name:
        last, first = name.split(",", 1)
        return f"{first} {last}"
    return name


def same_person(a: str, b: str, threshold: int = 90) -> bool:
    """Soyad aynı ve ad baş harfi uyumluysa aynı kişi kabul edilir."""
    na = normalize_name(_first_last_order(a)).split()
    nb = normalize_name(_first_last_order(b)).split()
    if not na or not nb:
        return False
    # 'Gursoy O' (soyad + baş harf) biçimini 'O Gursoy' sırasına çevir
    na = na[-1:] + na[:-1] if len(na) > 1 and len(na[-1]) == 1 else na
    nb = nb[-1:] + nb[:-1] if len(nb) > 1 and len(nb[-1]) == 1 else nb
    if na[-1] != nb[-1]:
        return fuzz.token_sort_ratio(" ".join(na), " ".join(nb)) >= threshold
    return na[0][0] == nb[0][0]
