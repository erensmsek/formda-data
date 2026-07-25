# formda-data

FormDa uygulamasının statik yemek ve egzersiz veri seti. Uygulama bu
JSON'ları GitHub raw üzerinden açılışta indirir; `version.json` değişince
güncellenen setleri çeker.

## Yapı

```
version.json          # sürüm takibi (uygulama değişeni buradan anlar)
foods/
  turkomp_v1.json     # 645  — TürKomp, laboratuvar analizli TR gıdalar
  usda_top5000_v1.json# 5000 — USDA FoodData Central (Foundation + SR Legacy)
  off_tr_v1.json      # 706  — Open Food Facts, TR barkodlu paketli ürünler
  popular_tr_foods_v1.json # 104 — elle derlenen popüler TR yemekleri
exercises/
  exercises_v1.json   # 873  — Free Exercise DB, TR çevirili (salon hareketleri)
  activities_v1.json  # 818  — Compendium of Physical Activities (spor dalları,
                      #        kardiyo ve günlük aktiviteler; MET değerleriyle)
  manifest.json       # dosya listesi + checksum + lisans
```

Yemek kayıtları 100 g başına makro içerir (şema: FormDa reposu
`scripts/schemas/food.schema.json`). Egzersiz kayıtları kas grubu, ekipman,
zorluk, TR talimatlar ve 2 kare görsel URL'i içerir.

## Bir seti güncellerken

1. İlgili JSON'u yenileyip `foods/` ya da `exercises/`'a koy.
2. `version.json`'da o setin `version` alanını artır (örn. `1.0.0` → `1.1.0`).
3. Push et. Uygulama sürüm farkını görüp yalnızca o seti yeniden indirir.

## Kaynaklar ve lisans / atıf

- **TürKomp** — Ulusal Gıda Kompozisyon Veritabanı
  (turkomp.tarimorman.gov.tr). Akademik atıf gerektirir; uygulamanın "Hakkında"
  ekranında kaynak olarak belirtilir.
- **USDA FoodData Central** (fdc.nal.usda.gov) — kamu malı, serbest kullanım.
- **Open Food Facts** (openfoodfacts.org) — veri **ODbL** (Open Database
  License) altındadır; **atıf zorunludur** ve uygulamanın "Hakkında" ekranında
  belirtilir. Ürün içerikleri Database Contents License kapsamındadır.
- **Free Exercise DB** (github.com/yuhonas/free-exercise-db) — **Unlicense**
  (kamu malı), ticari kullanım serbest. Egzersiz görselleri de aynı repodan
  raw URL ile referanslanır. Türkçe çeviriler Gemini ile üretilip elle
  gözden geçirilmiştir.
- **2024 Adult Compendium of Physical Activities**
  (https://pacompendium.com) — spor dalları ve günlük aktivitelerin MET
  değerleri. Ticari kullanım **serbest**, **atıf zorunludur**; uygulamanın
  "Hakkında" ekranında belirtilir.
  ⚠️ Lisans şartı: MET değerleri **değiştirilmez** ve farklı MET seviyesindeki
  aktiviteler **birleştirilmez**. Yalnızca açıklama metinleri Türkçeleştirilir
  (ölçü birimleri metrik sisteme çevrilir).
  Atıf: Herrmann SD, Willis EA, Ainsworth BE, et al. 2024 Adult Compendium of
  Physical Activities. *J Sport Health Sci.* 2024;13(1).

Veriler `FormDa/scripts/` altındaki üretim scriptleriyle oluşturulmuştur.
