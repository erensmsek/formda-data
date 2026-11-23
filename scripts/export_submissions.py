#!/usr/bin/env python3
"""Faz 9.6 — onaylanan EGZERSİZ katkılarını yayına çıkarır (9.6.11, 9.6.14, 9.6.16).

Supabase'den `status='approved'` egzersiz katkılarını çeker,
`exercises/community_exercises_v1.json`'ı üretir, `version.json`'ı bump'lar ve
Supabase'e `status='published'` yazar.

⚠️ Yemek katkıları artık Veri Paneli'nde (Faz 7, 23 Kas 2026): onay
`submission_approve` ile `catalog_foods`'a girer, `foods/community_tr_v1.json`'ı
panelin yayın hattı yazar. Bu betik o dosyaya DOKUNMAZ (iki yazar olmasın).
Egzersiz kısmı spor kataloğu (panel Faz 10) gelene kadar burada kalır.

**Neden curated'dan AYRI dosya**: curated set `build_curated_tr.py` ile
üretiliyor; elle eklenen kayıt bir sonraki üretimde sessizce silinirdi.
community_* dosyaları yalnız bu script tarafından yazılır.

`revoked` kayıtlar üretimde otomatik düşer — dosya her seferinde
`published` + `approved` kümesinden **baştan** üretilir, artımlı değil.

Ortam değişkenleri (GitHub Actions'ta secret):
    SUPABASE_URL           https://xxx.supabase.co
    SUPABASE_SERVICE_KEY   service_role anahtarı (ASLA log'a yazma)
    FORMDA_DATA            formda-data çalışma kopyasının yolu

Kullanım:
    python3 scripts/export_submissions.py --dry-run
    python3 scripts/export_submissions.py --apply
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DATA_ROOT = os.environ.get(
    'FORMDA_DATA', '/Volumes/e-ssd/ProjeKod/formda-data')
EX_OUT = os.path.join(DATA_ROOT, 'exercises/community_exercises_v1.json')
VERSION = os.path.join(DATA_ROOT, 'version.json')

# Yayına giren durumlar. 'revoked' ve 'rejected' burada YOK — dosya her
# seferinde baştan üretildiği için geri çekilen kayıt kendiliğinden düşer.
LIVE_STATUSES = ('approved', 'published')


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f'Ortam değişkeni eksik: {name}')
    return value


def _request(path: str, method: str = 'GET', body: dict | None = None,
             params: dict | None = None) -> list[dict]:
    url = _env('SUPABASE_URL').rstrip('/') + '/rest/v1/' + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    key = _env('SUPABASE_SERVICE_KEY')
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        # ⚠️ Anahtar log'a sızmasın: yalnızca durum kodu ve gövde yazılır.
        sys.exit(f'Supabase hatası {e.code}: {e.read().decode()[:300]}')


def fetch(table: str) -> list[dict]:
    return _request(table, params={
        'status': f'in.({",".join(LIVE_STATUSES)})',
        'select': '*',
        'order': 'submitted_at.asc',
    })


def exercise_record(row: dict) -> dict:
    return {
        'id': f'community_{row["id"]}',
        'name_tr': row['name_tr'].strip(),
        'name_en': row.get('name_en'),
        'alternative_names_tr': [],
        'category': row.get('category') or 'strength',
        'tracking_type': row.get('tracking_type') or 'reps',
        'primary_muscles': row.get('primary_muscles') or [],
        'secondary_muscles': [],
        'equipment': row.get('equipment') or [],
        'difficulty': row.get('difficulty') or 'unknown',
        'met_value': float(row['met_value']) if row.get('met_value') else None,
        'image_urls': [],
        'animation_url': None,
        'instructions_tr': row.get('instructions_tr') or [],
        'tips_tr': [],
        'muscle_map_regions': [],
        'source': 'community',
    }


def bump_version(key_path: tuple[str, str], path: str, count: int) -> str:
    with open(VERSION, encoding='utf-8') as f:
        v = json.load(f)
    section, key = key_path
    entry = v.setdefault(section, {}).setdefault(
        key, {'version': '1.0.0', 'count': 0})
    major, minor, patch = (int(x) for x in entry['version'].split('.'))
    entry['version'] = f'{major}.{minor}.{patch + 1}'
    entry['count'] = count
    entry['updated_at'] = datetime.date.today().isoformat()
    entry['checksum'] = 'sha256:' + hashlib.sha256(
        open(path, 'rb').read()).hexdigest()
    with open(VERSION, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
    return entry['version']


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error('--dry-run veya --apply verin')

    exercises = fetch('exercise_submissions')
    new_ex = [r for r in exercises if r['status'] == 'approved']

    print(f'egzersiz: {len(exercises)} yayında ({len(new_ex)} yeni onay)')
    for r in new_ex[:10]:
        print(f'    + {r["name_tr"][:48]}')

    if not args.apply:
        print('\n(kuru çalıştırma — dosya ve durum değişmedi)')
        return

    # ⚠️ "Yeni onay var mı" diye BAKILMAZ, üretilen içerik diskteki dosyayla
    # KARŞILAŞTIRILIR. Önceki sürüm yalnızca yeni onay varsa üretiyordu; geri
    # çekilen (`revoked`) kayıt yeni onay yaratmadığı için setten hiç
    # düşmüyordu (9.6.16 çalışmıyordu). İçerik karşılaştırması geri çekmeyi,
    # elle düzeltmeyi ve şema değişikliğini de kapsıyor.
    os.makedirs(os.path.dirname(EX_OUT), exist_ok=True)

    changed = []
    for label, path, payload, version_key, count in (
        ('community(exercises)', EX_OUT, [exercise_record(r) for r in exercises],
         ('exercises', 'community'), len(exercises)),
    ):
        rendered = json.dumps(payload, ensure_ascii=False, indent=1)
        current = None
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                current = f.read()
        if rendered == current:
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        changed.append(f'{label} → {bump_version(version_key, path, count)}')

    if not changed:
        print('\nDeğişiklik yok, üretim atlandı.')
    else:
        print('\n' + '   '.join(changed))

    # Durum geri yazma (9.6.14): panelde "yayında" rozeti, çift yayın önlenir.
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for r in new_ex:
        _request('exercise_submissions', method='PATCH',
                 params={'id': f'eq.{r["id"]}'},
                 body={'status': 'published', 'published_at': now})
    print(f'{len(new_ex)} kayıt published olarak işaretlendi.')


if __name__ == '__main__':
    main()
