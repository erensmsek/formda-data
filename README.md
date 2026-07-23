# formda-data

FormDa uygulamasının statik yemek (ve ileride egzersiz) veri seti. Uygulama bu
JSON'ları GitHub raw üzerinden açılışta indirir; `version.json` değişince
güncellenen setleri çeker.

## Yapı

```
version.json          # sürüm takibi (uygulama değişeni buradan anlar)
foods/
  turkomp_v1.json     # 645  — TürKomp, laboratuvar analizli TR gıdalar
  usda_top5000_v1.json# 5000 — USDA FoodData Central (Foundation + SR Legacy)
  off_tr_v1.json      # 706  — Open Food Facts, TR barkodlu paketli ürünler
```

Her kayıt 100 g başına makro içerir (şema: FormDa reposu
`scripts/schemas/food.schema.json`).

## Bir seti güncellerken

1. İlgili JSON'u yenileyip `foods/`'a koy.
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

Veriler `FormDa/scripts/` altındaki üretim scriptleriyle oluşturulmuştur.
