"""Değerlendirme yılı mantığı.

Kural: X yılında yapılan yayın ve atıflar için başvuru X+1 yılında yapılır.
Kullanıcıya iki seçenek gösterilir:
    * (bugünkü yıl - 1) verileri -> bugünkü yıl başvurusu
    * (bugünkü yıl) verileri     -> gelecek yıl başvurusu (erken hazırlık, ör. Aralık ayı)
Başvuru dönemi (Ocak-Mart) içindeysek önceki yıl, değilse içinde bulunulan yıl önerilir.
"""
from datetime import date

from app.models.schemas import YearOption

APPLICATION_SEASON_LAST_MONTH = 3  # Ocak-Mart arası "başvuru dönemi" kabul edilir


def year_options(today: date | None = None) -> list[YearOption]:
    today = today or date.today()
    y = today.year
    in_season = today.month <= APPLICATION_SEASON_LAST_MONTH

    previous = YearOption(
        data_year=y - 1,
        application_year=y,
        label=f"{y - 1} yılı yayın/atıfları  →  {y} başvurusu",
        recommended=in_season,
        hint=f"{y} yılında yapılacak başvuru için {y - 1} yılında yayımlanan makaleler ve "
        f"{y - 1} yılında alınan atıflar listelenir.",
    )
    current = YearOption(
        data_year=y,
        application_year=y + 1,
        label=f"{y} yılı yayın/atıfları  →  {y + 1} başvurusu",
        recommended=not in_season,
        hint=f"{y + 1} başvurusu için erken hazırlık. {y} yılı henüz bitmediği için yıl sonuna kadar "
        f"yeni yayın/atıf eklenebilir; Ocak ayında tekrar çalıştırmanız önerilir.",
    )
    return [previous, current]


def is_in_data_year(pub_year: int | None, data_year: int) -> bool:
    return pub_year is not None and pub_year == data_year
