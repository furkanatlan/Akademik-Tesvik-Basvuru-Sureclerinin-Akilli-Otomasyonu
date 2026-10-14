"""Web sayfasından işaretlenmiş (highlight) ve URL damgalı kanıt ekran görüntüsü (Sorumlu: Öğrenci 2).

Kılavuz s.10/13: "Ekran görüntüsünün alındığı web adresi belge üzerinde görülebilmelidir."
Bu yüzden her görüntünün üstüne kırmızı açıklama (label) + URL + tarih şeridi eklenir.

Temel gerçekleme hazırdır; siteye özel seçiciler (MJL, TR Dizin, dergi siteleri) Öğrenci 2 tarafından eklenir.
"""
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import Page, sync_playwright

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Sayfadaki metni bulup sarı arka planla işaretleyen JS (kılavuzdaki sarı vurgu)
_HIGHLIGHT_JS = """
(terms) => {
  let count = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const parent = node.parentElement;
    if (!parent || parent.tagName === "SCRIPT" || parent.tagName === "STYLE") continue;
    for (const term of terms) {
      const idx = term ? node.nodeValue.toLowerCase().indexOf(term.toLowerCase()) : -1;
      if (idx >= 0) {
        const range = document.createRange();
        range.setStart(node, idx);
        range.setEnd(node, idx + term.length);
        const mark = document.createElement("mark");
        mark.style.cssText = "background:#ffd400;color:inherit;padding:0 2px;border-radius:3px";
        range.surroundContents(mark);
        if (count === 0) mark.scrollIntoView({block: "center"});
        count++;
        break;
      }
    }
  }
  return count;
}
"""


def highlight_terms(page: Page, terms: list[str]) -> int:
    """Sayfada terimleri işaretler, bulunan adedi döndürür."""
    return page.evaluate(_HIGHLIGHT_JS, terms)


def stamp_header(png_path: Path, url: str, label: str) -> None:
    """Görüntünün üstüne kırmızı açıklama + URL + tarih şeridi ekler."""
    img = Image.open(png_path).convert("RGB")
    font = ImageFont.truetype(FONT_PATH, 18)
    small = ImageFont.truetype(FONT_PATH, 14)
    band_h = 64
    out = Image.new("RGB", (img.width, img.height + band_h), "white")
    out.paste(img, (0, band_h))
    draw = ImageDraw.Draw(out)
    draw.text((12, 8), label, fill=(220, 0, 0), font=font)
    draw.text((12, 38), f"{url}    ({datetime.now():%d.%m.%Y %H:%M})", fill=(40, 40, 40), font=small)
    draw.line([(0, band_h - 1), (img.width, band_h - 1)], fill=(200, 200, 200), width=1)
    out.save(png_path)


def capture(url: str, out_png: Path, terms: list[str], label: str, full_page: bool = False) -> int:
    """URL'yi açar, terimleri işaretler, ekran görüntüsü alır ve damgalar. Bulunan terim sayısını döndürür."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=USER_AGENT, locale="tr-TR", viewport={"width": 1366, "height": 900}
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=60_000)
        found = highlight_terms(page, terms) if terms else 0
        page.screenshot(path=str(out_png), full_page=full_page)
        browser.close()
    stamp_header(out_png, url, label)
    return found
