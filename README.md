# Akademik Teşvik Başvuru Süreçlerinin Akıllı Otomasyonu
**Metin İşleme ve Görsel Kanıt Oluşturma**

Akademisyenin adını alıp Google Scholar'dan yayın ve atıflarını bulan, seçilen yıla göre filtreleyen,
uygulama içindeki tarayıcıda yapılan WoS / Scopus kurum girişiyle dizin taramasını yapan ve
Burdur Mehmet Akif Ersoy Üniversitesi Akademik Teşvik Kılavuzu'na ([kilavuz.pdf](kilavuz.pdf)) uygun
**işaretlenmiş kanıt PDF'lerini** otomatik hazırlayan web uygulaması.

📘 **Proje rehberi, mimari, teknolojiler ve görev dağılımı:** [GOREV_DAGILIMI.md](GOREV_DAGILIMI.md)

## Hızlı başlangıç
```bash
git clone https://github.com/furkanatlan/Akademik-Tesvik-Basvuru-Sureclerinin-Akilli-Otomasyonu.git
cd Akademik-Tesvik-Basvuru-Sureclerinin-Akilli-Otomasyonu
cp .env.example .env                 # Windows PowerShell: copy .env.example .env
docker compose up -d --build         # ilk sefer 5-10 dk
docker compose exec backend python scripts/smoke_test.py   # tüm satırlar OK olmalı
```
- Uygulama: http://localhost:5173 (mock modda "Ahmet Yılmaz" arayın — örnek veriler kurgusaldır)
- API dokümantasyonu: http://localhost:8000/docs
- Gömülü tarayıcı (WoS / Scopus kurum girişi): uygulamanın 4. adımında görünür; doğrudan http://localhost:6080/vnc.html

## Servisler
| Servis | Görev | Port |
|---|---|---|
| frontend | React + Vite arayüz | 5173 |
| backend | FastAPI REST API | 8000 |
| worker | Celery: tarama, PDF işaretleme, birleştirme | — |
| browser | Paylaşımlı Chromium + noVNC: WoS/Scopus girişi ve oturumlu tarama | 6080 (yalnızca localhost) |
| db | PostgreSQL 16 (önbellek, iş geçmişi) | iç ağ |
| redis | İş kuyruğu | iç ağ |
| grobid | (opsiyonel) kaynakça ayrıştırma — `docker compose --profile grobid up -d grobid` | 8070 |
