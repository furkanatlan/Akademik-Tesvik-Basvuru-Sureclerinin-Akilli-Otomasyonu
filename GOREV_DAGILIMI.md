# Akademik Teşvik Başvuru Süreçlerinin Akıllı Otomasyonu
### Metin İşleme ve Görsel Kanıt Oluşturma — Proje Rehberi ve Görev Dağılımı

> Bu belge 4 proje öğrencisi için hazırlanmıştır. Önce **1–6. bölümleri herkes okusun**, sonra
> **8. bölümde** kendi görev listenize geçin. Görev listeleri **işlem önceliğine göre** sıralıdır;
> sırayı bozmayın, çünkü sonraki adımlar öncekilerin çıktısını kullanır.

---

## İçindekiler
1. [Uygulama ne yapacak?](#1-uygulama-ne-yapacak)
2. [Kılavuz analizi: sistemin uyması gereken kurallar](#2-kılavuz-analizi-sistemin-uyması-gereken-kurallar)
3. [Mimari](#3-mimari)
4. [Kullanılan teknolojiler ve kurulumlar (ne, neden)](#4-kullanılan-teknolojiler-ve-kurulumlar-ne-neden)
5. [Docker kullanımı](#5-docker-kullanımı)
6. [Modern ve güvenilir web scraping kuralları](#6-modern-ve-güvenilir-web-scraping-kuralları)
7. [Yol haritası ve ortak çalışma kuralları](#7-yol-haritası-ve-ortak-çalışma-kuralları)
8. [Görev dağılımı (4 öğrenci)](#8-görev-dağılımı)
9. [Entegrasyon, test ve teslim](#9-entegrasyon-test-ve-teslim)
10. [Riskler ve çözümleri](#10-riskler-ve-çözümleri)

---

## 1. Uygulama ne yapacak?

Akademisyen, akademik teşvik başvurusu için gereken **makale** ve **atıf** kanıt belgelerini,
Burdur Mehmet Akif Ersoy Üniversitesi *Akademik Teşvik Başvuru Sistemi Kılavuzu*'na
([kilavuz.pdf](kilavuz.pdf), Ocak/2024) uygun biçimde, **otomatik** hazırlar.

### Kullanıcı akışı (arayüz adımları)

| Adım | Ekran | Ne olur? |
|---|---|---|
| 1 | **Akademisyen** | Hoca ad-soyadını yazar → Google Scholar'da aranır. Aynı isimde birden fazla akademisyen varsa **fotoğraf, kurum, doğrulanmış e-posta alanı ve atıf sayısı** ile listelenir, hoca kendini seçer. Tek sonuç varsa bu adım otomatik geçilir. |
| 2 | **İşlem** | İki büyük seçenek: **"Makale belgelerini hazırla"** veya **"Atıf belgelerini hazırla"**. |
| 3 | **Yıl** | İki kart: *(bu yıl − 1) verileri → bu yıl başvurusu* ve *(bu yıl) verileri → gelecek yıl başvurusu*. Ocak–Mart arası önceki yıl, diğer aylarda içinde bulunulan yıl **"Önerilen"** olarak işaretlenir. Örn. Aralık 2026'da hazırlık yapan hoca **2026** verilerini (2027 başvurusu) seçer. |
| 4 | **Sonuçlar** | Seçilen yıla ait kayıtlar listelenir; her biri **Kabul / Kontrol gerekli / Kabul edilmez** rozeti ve gerekçesiyle gösterilir. "Hazırlanacak belgeler" açılınca kılavuzdaki belge listesi görünür. |
| 5 | **Belgeleri hazırla** | Arka planda her kayıt için PDF'ler indirilir, ilgili yerler **sarı işaretlenir**, kılavuzdaki **kırmızı açıklamalar** yazılır, dizin ekran görüntüleri alınır ve **her kayıt tek PDF** olarak birleştirilir. Hepsi ZIP olarak indirilir. |

**Yıl mantığının özeti:** X yılında yapılan yayın/atıflar için başvuru X+1 yılında yapılır.
- *Makalelerde*: yalnızca **basım (sayı) yılı = X** olan makaleler.
- *Atıflarda*: hocanın **eski yayınları dahil tüm yayınlarına**, **X yılında yayımlanmış** çalışmalarda yapılan atıflar.

---

## 2. Kılavuz analizi: sistemin uyması gereken kurallar

Bu kuralların kod karşılığı hazırdır: [backend/app/core/rules.py](backend/app/core/rules.py)
(testleri: [backend/tests/test_rules.py](backend/tests/test_rules.py)). Etiket metinleri kılavuzdaki kırmızı yazılarla birebir aynıdır.

### 2.1 Genel kurallar (kılavuz s.2)
- Belgelerin **yalnızca ilgili sayfaları** yüklenir (1500 sayfalık kitabın tamamı değil, ilgili sayfalar kesilir).
- Önemli yerler **boyanarak (sarı highlight) işaretlenir**, yanına kırmızı açıklama yazılır.
- Format dışı dosya iade edilir → çıktılar her zaman aynı düzende üretilmelidir.

### 2.2 MAKALE belgeleri (kılavuz s.3–7) — her makale için TEK PDF, bu sırayla

| Derginin dizini | 1. sayfa | 2. sayfa | 3+. sayfalar |
|---|---|---|---|
| **SCI / SCI-Expanded / SSCI / AHCI (ESCI)** | Makalenin ilk sayfası: **yayın yılı/tarihi** ve **başvuru sahibinin adı** işaretli (*"tarihin işaretlenmesi"*, *"ilgili yazarın işaretlenmesi"*) | **WoS Master Journal List** ekran görüntüsü, *"Science Citation Index Expanded"* (vb.) işaretli (*"sci indeksin işaretlenmesi"*) | Derginin *Editorial board* sayfası |
| **TR Dizin** | aynı | TR Dizin dergi kaydı ekran görüntüsü (yıl rozeti işaretli) | — |
| **Diğer uluslararası dizinler** (Scopus dahil) | aynı | Derginin **en az 5 yıldır** yayımlandığını gösteren kanıt (*"Founded: 2014"* vb.; arşivden de eklenebilir) | **Tarandığı dizinler** listesi + **editör/yayın kurulunun yabancı** olduğunu gösteren kısım (yabancı üye işaretli) |

### 2.3 ATIF belgeleri

**Yol A — "Atıfların doğrudan atıf yapan makaleler üzerinden gösterilmesi" (s.14–31)** → *sistemin ana yöntemi*.
Her atıf için TEK PDF:

| Atıf yapan çalışma | Belgeler (sırasıyla) |
|---|---|
| **SCI/SCIE/SSCI dergide makale** | 1) Atıf yapan makalenin **kaynakça** sayfası — hocanın yayını işaretli (*"atıf veren makalenin kaynakça kısmında atıf verilen makalenin işaretlenmesi"*) 2) Atıf yapan makalenin **ilk sayfası** 3) Derginin SCI olduğunu gösteren **MJL** ekran görüntüsü (işaretli) |
| **TR Dizin dergide makale** | 1) Kaynakça (işaretli) 2) İlk sayfa 3) *"atıf veren TRdizin derginin indeksini gösteren belge"* |
| **Diğer uluslararası hakemli dergide makale** | 1) Kaynakça (işaretli) 2) İlk sayfa 3) *"atıf veren makalenin uluslararası index olduğunu gösteren belge"* (Indexing sayfası) 4) *5 yıldır yayın yaptığını gösteren belge ve editör/yayın kurulu* |
| **Uluslararası kitap / kitap bölümü** | 1) Kitabın kaynakça sayfası (işaretli) 2) Kitap bölümünün ilk sayfası 3) *"uluslararası kitap olduğunu gösteren belge"* (yayınevi sayfası, ISBN) → **Kontrol gerekli** olarak işaretlenir |

**Yol B — WoS / Scopus veri tabanı üzerinden (s.9–13)**: Bu veri tabanları **kurum girişi** gerektirdiği için
otomatik taranmaz. Sistem kullanıcıya adım adım talimat verir, kullanıcı ekran görüntüsünü/PDF'i **yükler**, sistem OCR ile
şu filtrelerin belgede göründüğünü kontrol eder:
- WoS: `NOT Document Types: Early Access`, `NOT Researcher Profiles: <Soyad, Ad>`, `Web of Science Index: …`, `Publication Years: <yıl>`, sayfa URL'si.
- Scopus: `LIMIT-TO ( PUBYEAR , <yıl> )`, `EXCLUDE ( … <yazar> … )`, sayfa URL'si. Scopus listesindeki WoS/diğer dizin atıflarının dizini **ayrıca** belgelenir.

### 2.4 Kabul / ret kuralları (atıflar)

| Durum | Karar | Kaynak |
|---|---|---|
| Atıf yapan çalışmanın yılı ≠ seçilen yıl | **Ret** | Yıl kuralı |
| Başvuru sahibi, atıf yapan çalışmanın yazarı (**kendine atıf**) | **Ret** | s.10 madde 3, s.13 madde 2 |
| Atıf yapan çalışma **bildiri** (konferans/kongre/sempozyum) | **Ret** | Proje kuralı (aşağıdaki nota bakın) |
| Atıf yapan çalışma **erken görünümde** (Early Access saat simgeli / Article in Press; cilt-sayı yok) | **Ret** | s.10 madde 1, s.13 madde 1 |
| "Early Access" ibareli ama sayıya girmiş (iki tarih var) | **Kabul** — basım yılı esas | s.11 madde 2 |
| Atıf yapan çalışma tez, preprint vb. | **Ret** | — |
| Kitap / kitap bölümü | **Kontrol gerekli** (uluslararası mı?) | s.21–23 |
| Tür veya dizin tespit edilemedi | **Kontrol gerekli** | — |
| Dergi makalesi + dizin tespit edildi | **Kabul** | — |

> **Önemli yorum — bildiri kuralı:** Atıfı **yapan** çalışma bildiri ise atıf kabul edilmez. Atıf **alan** (hocanın)
> çalışma makale ya da bildiri olabilir; eski bir bildiriye bu yıl bir *dergi makalesinde* yapılan atıf kabul edilir.
> Kural farklı yorumlanırsa tek değişiklik yeri: `evaluate_citation()` — [rules.py](backend/app/core/rules.py).

### 2.5 Makale kabul kuralları
- Basım (sayı) yılı = seçilen yıl. Erken görünüm yılı farklıysa basım yılı esas alınır ve not düşülür.
- Cilt/sayı/sayfa bilgisi yoksa (henüz erken görünümde) → **Kontrol gerekli**.
- Bildiri, kitap vb. bu modülde hazırlanmaz → **Kontrol gerekli** (kılavuz s.32: proje/bildiri/sergi aynı mantıkla elle yüklenir).
- Dergi birden fazla dizindeyse en yüksek öncelikli olan kanıtlanır: SCIE > SSCI > AHCI > ESCI > Scopus > Diğer uluslararası > TR Dizin.

---

## 3. Mimari

```mermaid
flowchart LR
    U[Akademisyen<br/>Tarayıcı] -->|http://localhost:5173| FE[Frontend<br/>React + Vite]
    FE -->|/api proxy| API[Backend API<br/>FastAPI]
    API -->|iş kuyruğu| R[(Redis)]
    R --> W[Worker<br/>Celery]
    API --> DB[(PostgreSQL<br/>önbellek, iş geçmişi)]
    W --> DB
    subgraph Servisler [backend/app/services]
      S1[scholar + metadata<br/>Öğrenci 1]
      S2[index + evidence<br/>Öğrenci 2]
      S3[pdf<br/>Öğrenci 3]
    end
    API --> S1
    W --> S1 & S2 & S3
    S1 -->|Playwright / SerpAPI| GS[Google Scholar]
    S1 -->|REST| OA[OpenAlex / Crossref / Unpaywall]
    S2 -->|Playwright| IX[WoS MJL / TR Dizin / Scopus /<br/>Dergi siteleri / DergiPark]
    S3 --> FS[(./data<br/>PDF, PNG, ZIP)]
    W -.opsiyonel.-> GR[GROBID<br/>kaynakça ayrıştırma]
```

### 3.1 Veri akışı
```
Ad Soyad ──► search_authors ──► [kullanıcı seçer] ──► Yıl seçimi
                                                     │
        ┌───────────── Makale ───────────────────────┴──────────── Atıf ─────────────────────┐
        │ list_publications → yıl filtresi            list_publications (TÜM yıllar)          │
        │ enrich_publication (OpenAlex/Crossref)      → list_citing_works(yayın, YIL)          │
        │ resolve_indexes (MJL/TR Dizin/…)            → enrich_citing_work (makale mi bildiri mi?)│
        │ evaluate_publication → evidence_plan        → resolve_indexes → evaluate_citation      │
        └──────────────────────────────┬──────────────────────────────────────────────────────┘
                                       ▼
          Her EvidenceItem: PDF indir + sayfa kes + highlight + kırmızı etiket (pdf)
                            veya ekran görüntüsü + highlight + URL damgası (evidence)
                                       ▼
                    merge_pdfs → kayıt başına tek PDF → ZIP → arayüzden indir
```

### 3.2 Klasör yapısı ve sahiplik

```
.
├── docker-compose.yml          # tüm servisler (herkes; değişiklik PR ile)
├── .env.example                # ortam değişkenleri şablonu
├── kilavuz.pdf                 # MAKÜ kılavuzu (referans)
├── data/                       # üretilen dosyalar (git'e gitmez)
├── backend/
│   ├── Dockerfile, requirements.txt
│   ├── app/
│   │   ├── main.py, config.py, worker.py
│   │   ├── models/schemas.py   # ORTAK SÖZLEŞME (değişiklik = 4 onay)
│   │   ├── core/               # years.py, rules.py, names.py  (hazır; kural değişikliği ekipçe)
│   │   ├── api/                # REST uçları                    → Öğrenci 4
│   │   ├── pipeline/tasks.py   # Celery iş akışları             → Öğrenci 4
│   │   ├── services/scholar/   # Scholar sağlayıcıları          → Öğrenci 1
│   │   ├── services/metadata/  # OpenAlex/Crossref/Unpaywall    → Öğrenci 1
│   │   ├── services/index/     # dizin tespiti                  → Öğrenci 2
│   │   ├── services/evidence/  # web ekran görüntüsü + işaret   → Öğrenci 2
│   │   ├── services/pdf/       # PDF işaretleme/birleştirme     → Öğrenci 3
│   │   └── fixtures/mock_data.json  # kurgusal örnek veri       → Öğrenci 4 bakımını yapar
│   ├── scripts/smoke_test.py   # kurulum doğrulama
│   └── tests/
└── frontend/                   # React arayüzü                  → Öğrenci 4
    ├── Dockerfile, package.json, vite.config.ts
    └── src/ (App.tsx, components/, lib/api.ts)
```

### 3.3 Şu an hazır olanlar
- Docker ortamı (6 servis), tüm kütüphane ve sistem kurulumları, kurulum doğrulama betiği.
- Ortak veri modelleri, yıl mantığı, kılavuz kuralları ve testleri (9 test geçiyor).
- **Mock modunda tam çalışan arayüz** (yazar arama → seçim → işlem → yıl → sonuç listesi). Mock verisindeki kişiler kurgusaldır.
- Temel yardımcılar: PDF'te metin bulup sarı işaretleme + kırmızı etiket, sayfa kesme, PNG→PDF, birleştirme;
  web sayfasında metin işaretleme + URL/tarih damgalı ekran görüntüsü.
- `TODO(Öğrenci N)` yazan fonksiyonlar boş bırakılmıştır — görevleriniz bunlardır.

---

## 4. Kullanılan teknolojiler ve kurulumlar (ne, neden)

Hepsi Docker imajlarının içine kuruludur; bilgisayarınıza Python/Node kurmanız **gerekmez**.

### 4.1 Altyapı
| Bileşen | Sürüm | Nerede | Neden kuruldu |
|---|---|---|---|
| Docker + Docker Compose | Desktop güncel | Host | 4 kişinin birebir aynı ortamda çalışması; "bende çalışıyordu" sorununu ortadan kaldırır. |
| PostgreSQL | 16 | `db` servisi | Scholar/dizin sorgu **önbelleği** (aynı sayfayı tekrar çekmemek = engellenmemek), iş geçmişi, sonuçlar. |
| Redis | 7 | `redis` servisi | Celery iş kuyruğu ve iş durumu (ilerleme yüzdesi). |
| GROBID (opsiyonel) | 0.8.1 | `grobid` profili | Zor PDF'lerde kaynakça girdilerini koordinatlarıyla ayrıştırır; Öğrenci 3'ün yedek yöntemi. |

### 4.2 Backend (Python 3.12) — [backend/requirements.txt](backend/requirements.txt)
| Paket | Amaç |
|---|---|
| **FastAPI, Uvicorn, Pydantic, pydantic-settings** | REST API, otomatik dokümantasyon (`/docs`), tip güvenli veri modelleri, `.env` okuma. |
| **python-multipart** | Paywall'lı makalelerin PDF'ini veya WoS/Scopus raporunu kullanıcının yüklemesi. |
| **Celery + redis** | Dakikalar sürebilen tarama/PDF üretimini arka planda çalıştırmak; arayüz donmaz. |
| **SQLAlchemy, psycopg, Alembic** | Veritabanı erişimi ve şema göçleri (önbellek tablosu vb.). |
| **Playwright + Chromium** | JavaScript ile yüklenen sitelerin (Scholar, WoS MJL, TR Dizin, dergi siteleri) gerçek tarayıcıyla açılması, sayfada metnin **sarı işaretlenmesi** ve **ekran görüntüsü** alınması. |
| **httpx + tenacity** | OpenAlex, Crossref, Unpaywall, SerpAPI, Elsevier REST çağrıları; hata durumunda üstel bekleme ile yeniden deneme. |
| **curl_cffi** | Tarayıcı açmaya gerek olmayan statik sayfalarda (ör. DergiPark) gerçek tarayıcı TLS parmak izi ile hafif istek. |
| **BeautifulSoup4 + lxml** | HTML ayrıştırma (yazar kartları, dizin listeleri, yayın kurulu). |
| **PyMuPDF** | PDF'te metin arama (koordinatlarıyla), **highlight annotation**, kırmızı açıklama yazma, sayfa kesme, birleştirme. Projenin PDF çekirdeği. |
| **pypdf** | Yardımcı PDF işlemleri (bozuk PDF onarma, metadata). |
| **img2pdf** | Ekran görüntüsünü kayıpsız PDF sayfasına çevirme. |
| **ocrmypdf + pytesseract** | Taranmış (resim) PDF'lere metin katmanı ekleme; WoS/Scopus ekran görüntülerinde filtre ifadelerini okuma. |
| **Pillow** | Ekran görüntüsünün üstüne **URL + tarih + kırmızı açıklama** şeridi (kılavuz: "web adresi belge üzerinde görülebilmelidir"). |
| **rapidfuzz + unidecode** | Kaynakçada başlık için bulanık eşleştirme; "Gürsoy, O." = "Oğuz Gürsoy" gibi isim eşleştirme (kendine atıf tespiti). |
| **pytest, ruff** | Birim testler ve kod stili denetimi. |

### 4.3 Sistem paketleri (backend imajı)
| Paket | Amaç |
|---|---|
| `tesseract-ocr`, `tesseract-ocr-tur`, `tesseract-ocr-eng` | Türkçe + İngilizce OCR. |
| `ghostscript` | ocrmypdf'nin PDF optimizasyon adımları. |
| `fonts-dejavu-core` | PDF/ekran görüntüsüne **Türkçe karakterli** (ı, ş, ğ) etiket yazmak. |
| Chromium + bağımlılıkları | `playwright install --with-deps chromium` ile. |

### 4.4 Frontend — [frontend/package.json](frontend/package.json)
| Paket | Amaç |
|---|---|
| **React 18 + TypeScript** | Bileşen tabanlı, tip güvenli arayüz. |
| **Vite** | Hızlı geliştirme sunucusu; `/api` isteklerini backend'e yönlendirir (CORS gerekmez). |
| **Tailwind CSS** | Hızlı, tutarlı, sade görsel tasarım (MAKÜ moru `maku-*` renkleri tanımlı). |
| **TanStack Query** | API çağrıları, yükleniyor/hata durumları, iş ilerlemesini periyodik sorgulama. |
| **lucide-react** | İkonlar. |

### 4.5 Dış veri kaynakları
| Kaynak | Erişim | Ne için |
|---|---|---|
| Google Scholar | Playwright veya SerpAPI | Yazar arama (foto, kurum), yayın listesi, "Cited by" + yıl filtresi (`as_ylo/as_yhi`). |
| **OpenAlex** (ücretsiz API) | REST | Yayın türü (makale/bildiri), ISSN, cilt/sayı, atıf doğrulama (`filter=cites:W…,publication_year:YIL`), açık erişim PDF. |
| **Crossref** (ücretsiz API) | REST | DOI ile tür (`journal-article` / `proceedings-article`), basım vs. online yılı. |
| **Unpaywall** (ücretsiz API) | REST | Açık erişim PDF bağlantısı. |
| WoS Master Journal List | Playwright | SCIE/SSCI/AHCI/ESCI kanıtı (kılavuz s.5). |
| TR Dizin | Playwright | TR Dizin kanıtı (kılavuz s.20). |
| Scopus | Elsevier API veya Source List (xlsx) | Scopus kapsamı. |
| Dergi siteleri / DergiPark | Playwright / curl_cffi | Dizin listesi, kuruluş yılı, yayın kurulu. |

---

## 5. Docker kullanımı

### 5.1 İlk kurulum (herkes, bir kez)
Ön koşul: **Docker Desktop** (Windows'ta WSL2 açık, Settings → Resources → en az **6–8 GB RAM**) ve **Git**.

```bash
# 1) Repoyu klonla
git clone https://github.com/furkanatlan/Akademik-Tesvik-Basvuru-Sureclerinin-Akilli-Otomasyonu.git
cd Akademik-Tesvik-Basvuru-Sureclerinin-Akilli-Otomasyonu

# 2) Ortam dosyasını oluştur (Windows PowerShell: copy .env.example .env)
cp .env.example .env
#    .env içinde CONTACT_EMAIL'i kendi üniversite e-postanla değiştir.

# 3) İmajları derle ve tüm servisleri başlat (ilk sefer 5-10 dk sürer)
docker compose up -d --build

# 4) Kurulumu doğrula — tüm satırlar "OK" olmalı
docker compose exec backend python scripts/smoke_test.py

# 5) Testleri çalıştır
docker compose exec backend pytest -q
```

Sonra tarayıcıda:
- **Uygulama:** http://localhost:5173  (mock modda "Ahmet Yılmaz" arayarak akışı deneyin)
- **API dokümantasyonu (Swagger):** http://localhost:8000/docs
- Üretilen dosyalar: projedeki `data/` klasörü (smoke test çıktıları `data/smoke/`)

> Git Bash kullanıyorsanız ve `docker compose exec` komutlarında yol hatası alırsanız komutun başına
> `MSYS_NO_PATHCONV=1 ` ekleyin ya da PowerShell kullanın.

### 5.2 Her çalışma gününde TEKRARLANACAKLAR
```bash
git checkout main && git pull                 # 1) güncel kodu al
git checkout -b ogrenci1/yazar-arama          # 2) (yeni iş ise) kendi dalını aç / mevcut dalına geç: git checkout <dal>
git merge main                                 #    mevcut dalındaysan main'deki yenilikleri al
docker compose up -d                           # 3) servisleri başlat (kod değişikliği için tekrar build GEREKMEZ)
docker compose logs -f backend worker          # 4) (gerekirse) logları izle, Ctrl+C ile çık
# ... kod yaz ... backend kodu kaydedince API otomatik yeniden başlar, arayüz otomatik yenilenir
docker compose restart worker                  # 5) worker'ın kullandığı kodu değiştirdiysen (worker otomatik yenilenmez)
docker compose exec backend pytest -q          # 6) testler
docker compose exec backend ruff check .       # 7) stil denetimi
docker compose exec frontend npm run typecheck # 8) (frontend değiştiyse) tip denetimi
git add -A && git commit -m "Öğrenci1: yazar arama Playwright"   # 9) commit
git push -u origin <dal-adı>                   # 10) push → GitHub'da Pull Request aç
docker compose stop                            # 11) gün sonunda (veriler korunur)
```

### 5.3 Ne zaman ne yapmalı? (komut tablosu)

| Durum | Komut |
|---|---|
| `backend/requirements.txt` değişti (siz ya da arkadaşınız paket ekledi) | `docker compose build backend worker && docker compose up -d` |
| `frontend/package.json` değişti | `docker compose build frontend && docker compose up -d --renew-anon-volumes frontend` |
| `.env` değişti (ör. `SCHOLAR_PROVIDER=playwright`) | `docker compose up -d --force-recreate backend worker` |
| `docker-compose.yml` değişti | `docker compose up -d` |
| Container içinde komut satırı | `docker compose exec backend bash` |
| Python denemesi (ör. bir fonksiyonu elle çağırmak) | `docker compose exec backend python -c "from app.core.years import year_options; print(year_options())"` |
| Veritabanına bağlanmak | `docker compose exec db psql -U tesvik` |
| GROBID'i açmak (Öğrenci 3, gerekirse) | `docker compose --profile grobid up -d grobid` → http://localhost:8070 |
| Servislerin durumu | `docker compose ps` |
| Her şeyi durdurup silmek (DB verisi KALIR) | `docker compose down` |
| DB dahil sıfırlamak | `docker compose down -v` |
| Yeni paket eklemek (backend) | `requirements.txt`'ye **sürümüyle** ekle → yukarıdaki build komutu → PR'da belirt |
| Yeni paket eklemek (frontend) | `docker compose exec frontend npm install <paket>@<sürüm>` → `package.json` + `package-lock.json` commit |

### 5.4 Sık sorunlar
| Belirti | Çözüm |
|---|---|
| `port is already allocated` (8000/5173) | O portu kullanan programı kapatın veya `docker-compose.yml`'de sol taraftaki portu değiştirin (ör. `"8001:8000"`). Postgres/Redis dışarı açılmadığı için çakışmaz. |
| Kod değişikliği API'ye yansımıyor | `docker compose restart backend` (worker için `restart worker`). |
| Arayüz değişikliği yansımıyor | Tarayıcıda Ctrl+F5; olmazsa `docker compose restart frontend`. |
| `ModuleNotFoundError` | Biri `requirements.txt` değiştirmiştir → `docker compose build backend worker`. |
| Chromium çöküyor | Docker Desktop RAM'ini artırın (`shm_size` zaten 1 GB). |
| `.sh`/Python dosyalarında `\r` hataları | Repo `.gitattributes` ile LF kullanır; `git config --global core.autocrlf input` yapıp yeniden klonlayın. |

---

## 6. Modern ve güvenilir web scraping kuralları

Bu kurallar **Öğrenci 1 ve Öğrenci 2 için zorunludur.**

1. **Önce API, sonra resmi liste, en son tarayıcı.** OpenAlex/Crossref/Unpaywall/Elsevier API'leri ücretsiz ve kararlıdır; HTML kazımaya yalnızca API'de olmayan bilgi için (Scholar profil, MJL, TR Dizin, dergi sayfası) başvurun.
2. **Polite pool:** OpenAlex/Crossref/Unpaywall isteklerine `mailto=CONTACT_EMAIL` ekleyin.
3. **Önbellek zorunlu:** Her dış istek önce Postgres önbelleğine bakar (`CACHE_TTL_HOURS`). Geliştirme sırasında aynı sayfayı 50 kez çekmek = IP engeli.
4. **Hız sınırı:** Scholar ve dergi sitelerinde istekler arası `SCRAPE_MIN_DELAY_SEC`–`SCRAPE_MAX_DELAY_SEC` rastgele bekleme; **paralel istek yok**.
5. **Gerçekçi tarayıcı bağlamı:** Tek kalıcı Playwright context, güncel User-Agent, `tr-TR` locale, 1366×900 viewport; çerez bannerlarını kapatın.
6. **Sabit `sleep` yerine akıllı bekleme:** `page.wait_for_selector(...)`, `wait_until="networkidle"`.
7. **Yeniden deneme:** `tenacity` ile üstel bekleme (ör. 3 deneme, 2–30 sn); 429/503'te bekleyip tekrar.
8. **CAPTCHA'yı atlatmaya çalışmayın:** `gs_captcha` / "unusual traffic" görülürse işi durdurun, kullanıcıya bildirin ve SerpAPI'ye geçin (fallback).
9. **Seçicileri tek yerde tutun:** Her site için CSS seçicileri modülün başında sabit olarak; site değişince tek yer düzeltilir.
10. **Kayıtlı HTML ile test:** Testler canlı siteye gitmez; `tests/fixtures/html/` altına kaydedilmiş örnek sayfalar üzerinde çalışır.
11. **Hata ayıklama izi:** Başarısız taramada HTML ve ekran görüntüsünü `data/debug/` altına kaydedin.
12. **Kişisel veri:** Testlerde gerçek hocaların verisini repoya koymayın; mock veri kurgusaldır.

---

## 7. Yol haritası ve ortak çalışma kuralları

### 7.1 Yol haritası (8 hafta)

| Faz | Hafta | Öğrenci 1 (Veri) | Öğrenci 2 (Dizin/Web kanıt) | Öğrenci 3 (PDF) | Öğrenci 4 (Arayüz/API/Akış) | Kilometre taşı |
|---|---|---|---|---|---|---|
| 0 | 1 | Kurulum, kılavuz okuma | Kurulum, kılavuz okuma | Kurulum, kılavuz okuma | Kurulum, kılavuz okuma, mock arayüz | Herkeste smoke test OK |
| 1 | 2–3 | Önbellek + hız sınırlayıcı, yazar arama, yayın listesi | MJL, TR Dizin + işaretli ekran görüntüsü | PDF indirme, ilk sayfa işaretleme | Arayüz iyileştirme, dosya uçları, iş akışı iskeleti | **M1:** Gerçek yazar arama arayüzde |
| 2 | 4–5 | OpenAlex/Crossref zenginleştirme | Dergi sitesi/DergiPark: dizinler, kuruluş yılı, yayın kurulu | OCR, kaynakçada atıf bulma | **Makale** iş akışı uçtan uca | **M2:** Gerçek makale → tek PDF |
| 3 | 6–7 | Yıla göre atıf toplama, makale/bildiri sınıflandırma | Scopus, kitap kanıtı, `resolve_indexes` birleşimi | Birleştirme, ZIP, WoS/Scopus rapor doğrulama | **Atıf** iş akışı, elle yükleme, manuel düzeltme | **M3:** Gerçek atıflar → tek PDF'ler |
| 4 | 8 | Hata düzeltme | Hata düzeltme | Hata düzeltme | E2E test, demo | **M4:** 3 gönüllü hocayla gerçek deneme, rapor |

### 7.2 Ortak kurallar
- **Dal (branch) adı:** `ogrenciN/kisa-konu` (ör. `ogrenci2/mjl`). `main`'e doğrudan push yok; **Pull Request** + en az 1 arkadaş onayı.
- **Ortak sözleşme:** [schemas.py](backend/app/models/schemas.py) değişikliği ayrı bir PR'da yapılır ve **4 kişinin onayı** gerekir. Frontend'deki [api.ts](frontend/src/lib/api.ts) tipleri aynı PR'da güncellenir.
- **Kural değişikliği:** [rules.py](backend/app/core/rules.py) ve [years.py](backend/app/core/years.py) kılavuzla ilgilidir; değişiklik test eklenmeden birleştirilmez.
- **Herkes kendi klasöründe çalışır** (3.2'deki sahiplik); başkasının modülünde değişiklik gerekiyorsa o kişiye issue açın.
- **Mock-first:** Bir modül bitene kadar diğerleri mock veriyle çalışır; kimse kimseyi beklemez.
- **Testsiz PR yok:** Her yeni fonksiyon için en az bir `pytest` testi.
- **Haftalık toplantı:** Kilometre taşlarını gözden geçirin; engel varsa GitHub Issues'a yazın.

---

## 8. Görev dağılımı

Her öğrencinin listesi **Adım 0**'dan başlar ve sırayla ilerler. Her adımın sonunda **"Kontrol"** satırındaki
komut başarılı olmadan sonraki adıma geçmeyin. Her adım bitince 5.2'deki günlük döngüyle commit/PR yapın.

---

### 👤 Öğrenci 1 — Veri Toplama: Google Scholar + Metadata Zenginleştirme
**Sorumluluk:** Hocayı bulmak, yayınlarını ve seçilen yıldaki atıflarını toplamak; her kaydın **türünü (makale/bildiri)**,
yılını, cilt/sayısını, ISSN'ini ve PDF bağlantısını güvenilir kaynaklardan doğrulamak.
**Dosyalar:** `backend/app/services/scholar/*`, `backend/app/services/metadata/*`, `backend/app/services/cache.py` (yeni), `backend/tests/test_scholar_*.py`
**Teknolojiler:** Playwright (Python), httpx, tenacity, BeautifulSoup/lxml, OpenAlex/Crossref/Unpaywall API, SerpAPI, SQLAlchemy, rapidfuzz.

0. **Ortak kurulum** (5.1). Kılavuz s.1–2 ve s.8–31'i okuyun. [base.py](backend/app/services/scholar/base.py), [mock_provider.py](backend/app/services/scholar/mock_provider.py) ve [schemas.py](backend/app/models/schemas.py)'ı inceleyin.
   *Kontrol:* `docker compose exec backend python scripts/smoke_test.py` → tümü OK.
1. **Önbellek + hız sınırlayıcı** (`services/cache.py`): Postgres'te `http_cache(key, url, body, fetched_at)` tablosu (SQLAlchemy + Alembic göçü); `cached_get(url)` ve `polite_delay()` fonksiyonları. *Öğrenci 2 de bunu kullanacağı için ilk iş budur.*
   *Kontrol:* aynı URL iki kez istendiğinde ikincisi DB'den gelir (test).
2. **Yazar arama — Playwright** (`playwright_provider.search_authors`): `view_op=search_authors` sayfasından **ad, kurum, doğrulanmış e-posta alanı, fotoğraf URL'si, toplam atıf, ilgi alanları**. CAPTCHA tespiti → `ScholarBlockedError`.
   *Kontrol:* `.env`'de `SCHOLAR_PROVIDER=playwright` → `docker compose up -d --force-recreate backend worker` → arayüzde gerçek bir isim arayın; aynı isimli kişiler fotoğraf ve kurumuyla listelenmeli.
3. **SerpAPI sağlayıcısı + otomatik yedek:** `serpapi_provider.py` üç fonksiyon; Playwright `ScholarBlockedError` verirse ve `SERPAPI_KEY` varsa SerpAPI'ye geçiş (`get_provider` içinde).
   *Kontrol:* `SCHOLAR_PROVIDER=serpapi` ile aynı arama aynı sonucu verir.
4. **Yayın listesi** (`list_publications`): sayfalama (`cstart`, `pagesize=100`), başlık, yazarlar, dergi, yıl, `cites_id`/cited_by bağlantısı.
   *Kontrol:* Swagger'da `/api/authors/{id}/publications?year=...` doğru yılın yayınlarını döndürür.
5. **Yayın zenginleştirme** (`metadata/enrich.py → enrich_publication`): OpenAlex `search` + Crossref ile **DOI, work_type, ISSN/eISSN, volume/issue/pages, basım yılı (`published-print`) ve online yılı, publisher, homepage, pdf_url** (Unpaywall/OpenAlex `best_oa_location`). Eşleşme ölçütü: `rapidfuzz.token_set_ratio ≥ 92` ve yıl farkı ≤ 1.
   *Kontrol:* erken görünümü önceki yıl, basımı bu yıl olan bir makale doğru yılda listelenir ve gerekçede not görünür.
6. **Yıla göre atıf toplama** (`list_citing_works(pub, year)`): Scholar `cites=<id>&as_ylo=YIL&as_yhi=YIL` (tüm sayfalar) + OpenAlex `filter=cites:<W>,publication_year:YIL` ile çapraz kontrol; DOI/başlığa göre tekilleştirme. **Eski yayınlar dahil tüm yayınlar** taranır.
   *Kontrol:* 2015 yayınına 2026'da yapılan atıf, 2026 seçildiğinde listelenir; 2025 atıfı listelenmez.
7. **Makale/bildiri sınıflandırma** (`enrich_citing_work`) — *projenin en kritik kuralı*:
   Crossref `proceedings-article` veya OpenAlex `source.type = conference` veya kaynak adında *Proceedings, Conference, Symposium, Congress, Workshop, Kongre, Sempozyum, Bildiri* → `PROCEEDINGS`; `book-chapter`/`book` → `BOOK_CHAPTER`/`BOOK`; belirlenemezse `UNKNOWN` (arayüzde "Kontrol gerekli"). Ayrıca yazar listesini eksiksiz doldurun (kendine atıf tespiti buna bağlı).
   *Kontrol:* bildiri içindeki atıf arayüzde "Kabul edilmez – bildiri" gerekçesiyle görünür.
8. **Testler:** `tests/fixtures/html/scholar_*.html` kayıtlı sayfalarla ayrıştırıcı testleri; OpenAlex/Crossref yanıt örnekleri JSON olarak. Canlı istek atan test yok.
   *Kontrol:* `docker compose exec backend pytest -q` yeşil.

**Teslim ölçütü:** Gerçek bir hoca için yazar seçimi, yıl filtreli yayın listesi ve yıl filtreli atıf listesi (türleri doğru) arayüzde görünür.
**Bağımlılık:** Kimseyi beklemez. Çıktısını Öğrenci 2 (ISSN, homepage), Öğrenci 3 (pdf_url, başlık) ve Öğrenci 4 kullanır.

---

### 👤 Öğrenci 2 — Dizin (İndeks) Tespiti ve Web Kanıtları
**Sorumluluk:** Derginin hangi dizinde tarandığını bulmak ve kılavuzun istediği **web kanıtlarını** (MJL, TR Dizin, dizin listesi,
5 yıl kanıtı, yabancı yayın kurulu, uluslararası kitap) **işaretli + URL damgalı ekran görüntüsü** olarak üretmek.
**Dosyalar:** `backend/app/services/index/*`, `backend/app/services/evidence/*`, `backend/tests/test_index_*.py`
**Teknolojiler:** Playwright (ekran görüntüsü + DOM'da işaretleme), curl_cffi, BeautifulSoup, Pillow, httpx, Elsevier API (opsiyonel).

0. **Ortak kurulum** (5.1). Kılavuz s.4–7, 17, 20, 23, 26–27, 30–31'i okuyun. `data/smoke/screenshot.png`'yi açıp hazır `capture()` fonksiyonunun çıktısını inceleyin ([screenshot.py](backend/app/services/evidence/screenshot.py)).
   *Kontrol:* smoke test OK.
1. **Ortak ekran görüntüsü altyapısını güçlendirin** (`evidence/screenshot.py`): çerez banner kapatma, belirli bir öğeye kırpma (`element.screenshot`), birden fazla terim, tam sayfa seçeneği, `data/debug/` hata kaydı. Öğrenci 1'in `cached_get`/`polite_delay` fonksiyonlarını kullanın (hazır değilse geçici basit bekleme).
   *Kontrol:* `docker compose exec backend python -c "from pathlib import Path; from app.services.evidence.screenshot import capture; print(capture('https://example.org', Path('/data/test.png'), ['Example'], 'deneme'))"` → `data/test.png` işaretli ve URL damgalı.
2. **WoS Master Journal List** (`index/mjl.py`): ISSN ile arama, "Web of Science Core Collection" alanından SCIE/SSCI/AHCI/ESCI tespiti, ilgili ifadenin **sarı işaretli** ekran görüntüsü + etiket *"… indeksi gösteren belge – indeksin işaretlenmesi"* (kılavuz s.5, s.17).
   *Kontrol:* "Energy Conversion and Management" (ISSN 0196-8904) → `SCIE` ve işaretli görüntü.
3. **TR Dizin** (`index/trdizin.py`): dergi adı/ISSN ile arama, hangi yıllarda tarandığı (yeşil yıl rozetleri), işaretli ekran görüntüsü (kılavuz s.20).
   *Kontrol:* bilinen bir TR Dizin dergisi için seçilen yıl "taranıyor" çıkar.
4. **Dergi sitesi / DergiPark tarayıcı** (`index/journal_site.py`): ana sayfadan *Index/Indexing/Abstracting/Dizinler*, *Editorial Board/Yayın Kurulu*, *Archive/Arşiv*, *About* sayfalarını bulun; DergiPark için özel ayrıştırıcı (`/indexes`, `/board`, `/archive`). **Kuruluş yılı** (`Founded/Since/Başlangıç` veya arşivdeki ilk cilt yılı) → `founded_year`; yaş ≥ 5 kontrolü (kılavuz s.7, s.27).
   *Kontrol:* örnek dergide dizin listesi, kuruluş yılı ve yayın kurulu sayfası URL'leri doğru.
5. **Yabancı yayın kurulu tespiti** (`foreign_board_members`): yayın kurulu satırlarında Türkiye dışındaki ülke/üniversite adlarını bulun (ülke adı listesi TR+EN), bu satırları işaretleyen görüntü + etiket *"editör/yayın kurulunun yabancı olduğunu gösteren kısım"*.
6. **Scopus** (`index/scopus.py`): `ELSEVIER_API_KEY` varsa Serial Title API; yoksa Scopus Source List xlsx'ini `data/cache/` altına indirip ISSN ile eşleştirme. Kanıt: Scopus kaynak sayfası veya derginin Scopus'u gösteren dizin sayfası.
7. **Uluslararası kitap kanıtı:** yayınevi sayfasında ISBN/yayınevi bilgisini işaretleyen görüntü (kılavuz s.23).
8. **`resolve_indexes` birleşimi:** MJL → Scopus → dergi sitesi → TR Dizin sırasıyla, sonuçları önbelleğe alarak `JournalInfo.indexes`, `index_evidence_urls`, `founded_year` doldurun. Ayrıca `capture_evidence(item: EvidenceItem, out_dir) -> Path` fonksiyonu (Öğrenci 4 akışta çağıracak): `INDEX_SCREENSHOT`, `FOUNDED_YEAR_SCREENSHOT`, `EDITORIAL_BOARD_SCREENSHOT`, `BOOK_PROOF_SCREENSHOT` türlerini üretir.
9. **Testler:** kayıtlı HTML'lerle ayrıştırıcı testleri (`tests/fixtures/html/mjl_*.html`, `trdizin_*.html`, `dergipark_*.html`).

**Teslim ölçütü:** SCIE, TR Dizin ve "diğer uluslararası" birer örnek dergi için kılavuzdaki görünüme benzer işaretli, URL damgalı kanıt görüntüleri otomatik üretilir.
**Bağımlılık:** ISSN/homepage için Öğrenci 1 (o hazır olana kadar elle ISSN verin). Çıktısını Öğrenci 3 (PNG→PDF) ve Öğrenci 4 kullanır.

---

### 👤 Öğrenci 3 — PDF İşleme: Bulma, İşaretleme, Kesme, Birleştirme
**Sorumluluk:** Makale PDF'lerini indirmek; ilk sayfada **yılı ve hocanın adını**, atıf yapan makalenin **kaynakçasında hocanın yayınını**
bulup sarı işaretlemek; kılavuzdaki kırmızı açıklamaları yazmak; yalnızca ilgili sayfaları kesip ekran görüntüleriyle birlikte
**kayıt başına tek PDF** ve ZIP üretmek; yüklenen WoS/Scopus raporlarını doğrulamak.
**Dosyalar:** `backend/app/services/pdf/*` (`fetch.py`, `ocr.py`, `highlight.py`, `references.py`, `assemble.py`, `validate.py`), `backend/tests/test_pdf_*.py`, `backend/tests/fixtures/pdf/`
**Teknolojiler:** PyMuPDF, ocrmypdf + Tesseract (tur+eng), img2pdf, rapidfuzz, unidecode, httpx/Playwright (indirme), GROBID (opsiyonel).

0. **Ortak kurulum** (5.1). Kılavuz s.2, 4, 6, 15–16, 18–19, 21–22, 24–25'i okuyun. `data/smoke/pdf_highlight.pdf` ve `birlesik_ornek.pdf`'yi açın; [highlight.py](backend/app/services/pdf/highlight.py) ve [assemble.py](backend/app/services/pdf/assemble.py)'deki hazır fonksiyonları inceleyin.
   *Kontrol:* smoke test OK.
1. **Test PDF seti:** `tests/fixtures/pdf/` altına 5–6 **açık erişimli** makale (Elsevier/Springer/DergiPark/IEEE farklı düzenler) + 1 taranmış (resim) PDF koyun.
2. **PDF indirme** (`fetch.py → download_pdf(url, dst)`): httpx ile indirme, `%PDF` imza kontrolü; yayıncı yönlendirmelerinde Playwright `page.expect_download()`; başarısızsa `PdfUnavailableError` (arayüz "PDF'i elle yükleyin" diyecek).
   *Kontrol:* OA bir DOI'nin `pdf_url`'sinden PDF iner.
3. **Metin katmanı + OCR** (`ocr.py → ensure_text_layer(pdf)`): metin yoksa `ocrmypdf --language tur+eng --skip-text`.
   *Kontrol:* taranmış PDF'te `page.search_for()` sonuç verir.
4. **İlk sayfa işleme** (`process_first_page(pdf, year, author_name) -> Path`): sayfanın üst kısmındaki (künye/başlık bölgesi) **yayın yılını** ve yazar bloğundaki **hocanın adını** (`core.names.name_variants` ile tüm biçimler: "Gürsoy O", "O. Gürsoy", Türkçe karaktersiz hâli) sarı işaretleyin; *"tarihin işaretlenmesi"* ve *"ilgili yazarın işaretlenmesi"* kırmızı etiketleri; sadece 1. sayfayı çıkarın (kılavuz s.4, s.6).
   *Kontrol:* 5 farklı düzende yıl ve ad doğru işaretli.
5. **Kaynakçada atıfı bulma** (`references.py → find_reference_entry`) — *en zor görev*:
   "References / Kaynakça / Kaynaklar / Bibliography / Literature Cited" başlığından sonrasını tarayın; satırları birleştirip tire/ligatür (ﬁ, ﬂ) normalizasyonu yapın; hocanın yayın başlığını `rapidfuzz.partial_ratio` ile arayın; bulunamazsa *soyad + yıl + dergi* ile; eşleşen girdinin **tüm satırlarını** işaretleyin. Zor durumlarda GROBID (`/api/processFulltextDocument`, `teiCoordinates=biblStruct`).
   *Kontrol:* test setindeki 6 makalenin en az 5'inde doğru girdi işaretlenir.
6. **Atıf PDF'i:** kaynakça sayfası(ları) (işaretli + *"atıf veren makalenin kaynakça kısmında atıf verilen makalenin işaretlenmesi"*) + atıf yapan makalenin ilk sayfası (*"atıf veren makalenin ilk sayfası"*) — sadece bu sayfalar (kılavuz s.15–16, 18–19).
7. **Birleştirme ve dosyalama** (`assemble.py`): `EvidenceItem.order` sırasıyla PDF parçaları + Öğrenci 2'nin PNG'leri (`png_to_pdf`) → kayıt başına tek PDF; isimlendirme `assemble.py` başındaki şablona göre; tümünü ZIP'leme (`build_zip(out_dir) -> Path`).
8. **WoS/Scopus rapor doğrulama** (`validate.py`): yüklenen PDF/PNG'de OCR ile `rules.database_citation_checklist()` ifadelerinin varlığını kontrol edip eksikleri listeleyin (kılavuz s.10–13).
9. **Testler:** her fonksiyon için fixture PDF'lerle test.

**Teslim ölçütü:** Bir makale ve bir atıf için kılavuzdaki örneklere görsel olarak benzeyen, sadece ilgili sayfaları içeren tek PDF'ler üretilir.
**Bağımlılık:** `pdf_url` için Öğrenci 1 (o zamana kadar elle verilen PDF'lerle çalışın), PNG'ler için Öğrenci 2. Çıktısını Öğrenci 4 kullanır.

---

### 👤 Öğrenci 4 — Arayüz, API ve Uçtan Uca İş Akışı (Entegrasyon)
**Sorumluluk:** Kullanıcının gördüğü her şey (sade, açıklayıcı arayüz), REST uçları, arka plan işleri ve diğer üç modülün
**birleştirilmesi**; elle yükleme ve manuel düzeltme; uçtan uca testler ve demo.
**Dosyalar:** `frontend/*`, `backend/app/api/*`, `backend/app/pipeline/tasks.py`, `backend/app/worker.py`, `backend/app/fixtures/mock_data.json`, `backend/tests/test_api_*.py`
**Teknolojiler:** React + TypeScript + Vite + Tailwind + TanStack Query, FastAPI, Celery + Redis, SQLAlchemy, Playwright (E2E test).

0. **Ortak kurulum** (5.1). Kılavuzun tamamına göz atın. Arayüzü mock modda (`SCHOLAR_PROVIDER=mock`) uçtan uca deneyin (http://localhost:5173, "Ahmet Yılmaz"). [App.tsx](frontend/src/App.tsx), [steps.tsx](frontend/src/components/steps.tsx), [ResultsStep.tsx](frontend/src/components/ResultsStep.tsx), [api.ts](frontend/src/lib/api.ts), [routes_*.py](backend/app/api/) dosyalarını inceleyin.
   *Kontrol:* 4 adım çalışıyor; "Belgeleri hazırla" şu an `TODO(Öğrenci 4)` hatası veriyor (beklenen).
1. **Mock veriyi zenginleştirin** (`fixtures/mock_data.json`): her kural için örnek (bildiri, kendine atıf, erken görünüm, kitap, TR Dizin, diğer uluslararası) — diğerleri bu veriyle geliştirir.
2. **Arayüz iyileştirmeleri:** yükleniyor iskeletleri, anlaşılır hata mesajları (ör. "Scholar geçici olarak erişimi kısıtladı"), boş durumlar, mobil görünüm, klavye erişilebilirliği, yıl ekranında "yıl henüz bitmedi" uyarısı; Scholar fotoğrafı yoksa baş harf avatarı (hazır).
   *Kontrol:* `docker compose exec frontend npm run typecheck` temiz; telefon genişliğinde (DevTools) düzgün.
3. **Dosya uçları:** `GET /api/files/{yol}` (yalnızca `DATA_DIR` altı, yol kaçışı engelli), ZIP indirme, arayüzde **PDF önizleme** (iframe).
4. **Makale iş akışı** (`pipeline/tasks.py → prepare_articles`): 3.1'deki akış; `self.update_state(state="PROGRESS", meta={progress, message})` ile adım adım ilerleme; bir kayıtta hata olursa diğerlerine devam edip raporlama; çıktı listesi `output_files`.
   *Kontrol:* gerçek bir makale için tek PDF iner (M2).
5. **Elle yükleme:** `POST /api/uploads` (PDF/PNG) — PDF'i indirilemeyen (paywall) kayıtlar ve WoS/Scopus raporları için; arayüzde ilgili satırda "PDF yükle" düğmesi. Yüklenen dosya akışta otomatik kullanılır.
6. **Atıf iş akışı** (`prepare_citations`): tüm yayınlar → yıl filtreli atıflar → değerlendirme → kabul edilenler için belge üretimi; arayüzde atıflar "atıf alan yayınınız" başlığı altında gruplu (hazır).
   *Kontrol:* gerçek bir hoca için atıf PDF'leri iner (M3).
7. **Manuel düzeltme:** "Kontrol gerekli" satırlarında kullanıcı türü (makale/bildiri/kitap) ve dizini seçebilsin; karar yeniden hesaplansın (`POST /api/evaluate`).
8. **WoS/Scopus yolu (Yol B) ekranı:** kılavuz s.10–13'teki adımları görsel talimat olarak gösteren sayfa + rapor yükleme + Öğrenci 3'ün doğrulama sonucu.
9. **Kalıcılık:** iş geçmişi tablosu (hangi hoca, hangi yıl, hangi dosyalar) ve "önceki işlerim" listesi.
10. **Testler ve demo:** API testleri (`TestClient`), Playwright ile E2E senaryo (yazar ara → seç → yıl → belge), README güncelleme, demo videosu/sunumu.

**Teslim ölçütü:** Teknik bilgisi olmayan bir hoca, yardım almadan 5 dakikada kendi makale ve atıf dosyalarını indirebilir.
**Bağımlılık:** Başta mock veriyle bağımsız çalışır; 4. adımdan itibaren 1–3. öğrencilerin fonksiyonlarını çağırır (imzalar [schemas.py](backend/app/models/schemas.py) ve modül dosyalarında tanımlı).

---

## 9. Entegrasyon, test ve teslim

| Kontrol | Komut / Yöntem | Sorumlu |
|---|---|---|
| Kurulum | `docker compose exec backend python scripts/smoke_test.py` | Herkes |
| Birim testler | `docker compose exec backend pytest -q` | Herkes |
| Stil | `docker compose exec backend ruff check .` | Herkes |
| Frontend tipleri | `docker compose exec frontend npm run typecheck` | Öğrenci 4 |
| Kural testleri | [test_rules.py](backend/tests/test_rules.py) — her yeni kural için test | Değiştiren |
| Gerçek veri denemesi | 3 gönüllü hoca (farklı alan: mühendislik, sağlık, sosyal) | Ekip |
| Görsel kontrol | Üretilen PDF'ler kılavuzdaki örneklerle yan yana karşılaştırılır | Öğrenci 3 + 2 |

**Final teslim listesi:** çalışan Docker ortamı · makale ve atıf modülleri · örnek çıktı ZIP'i · test raporu · proje raporu · demo.

---

## 10. Riskler ve çözümleri

| Risk | Etki | Çözüm |
|---|---|---|
| Google Scholar CAPTCHA / IP engeli | Veri gelmez | Önbellek, yavaş tarama, SerpAPI yedeği, OpenAlex çapraz kaynağı. |
| Makale PDF'i paywall arkasında | İlk sayfa/kaynakça üretilemez | Unpaywall/OpenAlex OA bağlantısı; olmazsa kullanıcı PDF'i yükler (kurum ağından indirip). |
| WoS/Scopus kurum girişi ister | Yol B otomatik yapılamaz | Yol A (doğrudan makaleler) ana yöntem; Yol B için talimat + yükleme + OCR doğrulama. |
| MJL / TR Dizin site yapısı değişir | Dizin tespiti bozulur | Seçiciler tek yerde, kayıtlı HTML testleri, hata ayıklama kaydı. |
| Taranmış PDF | Metin bulunamaz | ocrmypdf (tur+eng). |
| Kaynakça stili çok farklı | Atıf işaretlenemez | Bulanık eşleştirme + soyad/yıl yedeği + GROBID; bulunamazsa "Kontrol gerekli". |
| Makale/bildiri yanlış sınıflandırılır | Yanlış kabul/ret | Crossref + OpenAlex + ad kalıpları; emin değilse "Kontrol gerekli" + manuel düzeltme. |
| Aynı isimli akademisyen | Yanlış kişi | Fotoğraf + kurum + e-posta alanı ile kullanıcı seçimi; kendine atıf tespitinde isim eşleştirmesine ek olarak Scholar/OpenAlex yazar kimliği de kullanılmalı (Öğrenci 1). |
