# Backend + Worker imajı: FastAPI, Celery, Playwright(Chromium), PyMuPDF, Tesseract OCR
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    TZ=Europe/Istanbul

# Sistem paketleri:
#  tesseract-ocr(+tur,+eng) : taranmış (resim) PDF'lerde metin bulmak için OCR
#  ghostscript              : ocrmypdf'nin PDF/A ve optimizasyon adımları için
#  fonts-dejavu-core        : PDF/ekran görüntüsü üzerine Türkçe karakterli etiket yazmak için
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-tur tesseract-ocr-eng \
        ghostscript fonts-dejavu-core curl tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN mkdir -p /data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
