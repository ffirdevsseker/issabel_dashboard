#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sporthink Cagri Merkezi - 90 Gunluk Seed Data Generator (Senaryo Uyumlu)
Calistirma: python backend/seed/seed_90gun.py
"""
import sys
import io
import json
import random
import uuid
import bcrypt
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values, Json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

random.seed(42)

# ── CONFIG ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "dashboard",
    "user": "dashboard_user",
    "password": "Dashboard2026!",
}

try:
    TZ = ZoneInfo("Europe/Istanbul")
except Exception:
    # Fallback to local timezone if tzdata is not installed
    TZ = datetime.now().astimezone().tzinfo
BASLANGIC = date(2026, 2, 4)
BITIS = date(2026, 5, 4)
MUSTERI_SAYISI = 3000
TARGET_CALLS = 32000
SIFRE = "Sporthink2026!"
JSON_PATH = Path(__file__).parent / "seed_content.json"

# ── TATIL & KAMPANYA GUNLERI ──────────────────────────────────────────────
HOLIDAYS = {
    date(2026, 4, 23),
    date(2026, 5, 1),
}

SPECIAL_DAYS = {
    date(2026, 2, 14): 1.30,
    date(2026, 3, 8): 1.25,
    date(2026, 4, 1): 1.50,
    date(2026, 4, 2): 1.50,
    date(2026, 4, 3): 1.50,
    date(2026, 5, 3): 1.40,
}

SPECIAL_FORCE_OPEN = {
    date(2026, 3, 8),
    date(2026, 5, 3),
}

# ── DAGILIMLAR ────────────────────────────────────────────────────────────
CALL_RANGES = {
    "mon": (450, 550),
    "tue_thu": (380, 450),
    "fri": (300, 380),
    "sat": (120, 180),
    "campaign": (600, 750),
}

CALL_DIRECTION_WEIGHTS = {
    "gelen": 0.85,
    "giden": 0.12,
    "dahili": 0.03,
}

CALL_RESULT_WEIGHTS = {
    "cevaplandi": 0.72,
    "aktarildi": 0.18,
    "cevaplanmadi": 0.07,
    "mesgul": 0.03,
}

CATEGORY_WEIGHTS = {
    "bilgi": 0.35,
    "satis": 0.25,
    "sikayet": 0.15,
    "teknik": 0.15,
    "diger": 0.10,
}

CATEGORY_DURATION = {
    "bilgi": (60, 180),
    "satis": (180, 360),
    "sikayet": (300, 900),
    "teknik": (240, 600),
    "diger": (120, 300),
}

CSAT_WEIGHTS = {
    5: 0.40,
    4: 0.35,
    3: 0.15,
    2: 0.06,
    1: 0.04,
}

TRANSFER_DEPT_WEIGHTS = {
    "Muhasebe": 0.35,
    "E-Ticaret": 0.30,
    "Depo/Stok": 0.25,
    "Bilgi İşlem": 0.10,
}

TICKET_CATS = ["hat", "sistem", "donanim", "yazilim", "diger"]
TICKET_CAT_WEIGHTS = [0.25, 0.30, 0.20, 0.15, 0.10]
TICKET_STATUS = ["open", "working", "resolved"]
TICKET_PRIORITY = ["high", "medium", "low"]

SEGMENTS = [
    (time(9, 0), time(10, 0), 0.05),
    (time(10, 0), time(12, 0), 0.25),
    (time(12, 0), time(13, 30), 0.10),
    (time(13, 30), time(16, 0), 0.30),
    (time(16, 0), time(18, 0), 0.22),
    (time(18, 0), time(19, 0), 0.08),
]

# ── KADRO ─────────────────────────────────────────────────────────────────
ADMIN_USERS = [
    {
        "username": "emre.kaya",
        "name": "Emre Kaya",
        "role": "admin",
        "departman": None,
        "ekip": None,
        "shift": (time(8, 30), time(18, 30)),
        "extension": "1",
    }
]

SUPERVISORS = [
    {
        "username": "ayse.demir",
        "name": "Ayşe Demir",
        "role": "supervisor",
        "departman": "Müşteri Hizmetleri",
        "ekip": "MH Ekip A",
        "shift": (time(9, 0), time(18, 0)),
        "extension": "10",
    },
    {
        "username": "murat.ozturk",
        "name": "Murat Öztürk",
        "role": "supervisor",
        "departman": "Müşteri Hizmetleri",
        "ekip": "MH Ekip B",
        "shift": (time(10, 0), time(19, 0)),
        "extension": "11",
    },
]

MH_PERSONEL = [
    {"username": "zeynep.yilmaz", "name": "Zeynep Yılmaz", "ekip": "MH Ekip A", "shift": (time(9, 0), time(18, 0)), "xp": 4820, "tier": "gumus", "extension": "100"},
    {"username": "ahmet.celik", "name": "Ahmet Çelik", "ekip": "MH Ekip A", "shift": (time(9, 0), time(18, 0)), "xp": 3150, "tier": "gumus", "extension": "101"},
    {"username": "elif.sahin", "name": "Elif Şahin", "ekip": "MH Ekip A", "shift": (time(9, 0), time(18, 0)), "xp": 5240, "tier": "altin", "extension": "102"},
    {"username": "can.arslan", "name": "Can Arslan", "ekip": "MH Ekip A", "shift": (time(9, 0), time(18, 0)), "xp": 1680, "tier": "gumus", "extension": "103"},
    {"username": "selin.koc", "name": "Selin Koç", "ekip": "MH Ekip A", "shift": (time(9, 0), time(18, 0)), "xp": 780, "tier": "bronz", "extension": "104"},
    {"username": "burak.yildiz", "name": "Burak Yıldız", "ekip": "MH Ekip B", "shift": (time(10, 0), time(19, 0)), "xp": 6890, "tier": "altin", "extension": "105"},
    {"username": "deniz.aksoy", "name": "Deniz Aksoy", "ekip": "MH Ekip B", "shift": (time(10, 0), time(19, 0)), "xp": 2340, "tier": "gumus", "extension": "106"},
    {"username": "fatma.erdogan", "name": "Fatma Erdoğan", "ekip": "MH Ekip B", "shift": (time(10, 0), time(19, 0)), "xp": 3980, "tier": "gumus", "extension": "107"},
    {"username": "gokhan.polat", "name": "Gökhan Polat", "ekip": "MH Ekip B", "shift": (time(10, 0), time(19, 0)), "xp": 950, "tier": "bronz", "extension": "108"},
    {"username": "hande.korkmaz", "name": "Hande Korkmaz", "ekip": "MH Ekip B", "shift": (time(10, 0), time(19, 0)), "xp": 15200, "tier": "platin", "extension": "109"},
]

OTHER_PERSONEL = [
    {"username": "kemal.dogan", "name": "Kemal Doğan", "departman": "Muhasebe", "shift": (time(9, 0), time(18, 0)), "extension": "200"},
    {"username": "neslihan.acar", "name": "Neslihan Acar", "departman": "Muhasebe", "shift": (time(9, 0), time(18, 0)), "extension": "201"},
    {"username": "oguz.tuncer", "name": "Oğuz Tuncer", "departman": "E-Ticaret", "shift": (time(9, 0), time(18, 0)), "extension": "210"},
    {"username": "pinar.sen", "name": "Pınar Şen", "departman": "E-Ticaret", "shift": (time(9, 0), time(18, 0)), "extension": "211"},
    {"username": "serkan.aydin", "name": "Serkan Aydın", "departman": "Depo/Stok", "shift": (time(9, 0), time(18, 0)), "extension": "220"},
    {"username": "tugba.kurt", "name": "Tuğba Kurt", "departman": "Depo/Stok", "shift": (time(9, 0), time(18, 0)), "extension": "221"},
    {"username": "volkan.tas", "name": "Volkan Taş", "departman": "Bilgi İşlem", "shift": (time(9, 0), time(18, 0)), "extension": "230"},
    {"username": "yasemin.bulut", "name": "Yasemin Bulut", "departman": "Bilgi İşlem", "shift": (time(9, 0), time(18, 0)), "extension": "231"},
]

USER_SEEDS = ADMIN_USERS + SUPERVISORS + [
    {**p, "role": "personel", "departman": "Müşteri Hizmetleri"} for p in MH_PERSONEL
] + [
    {**p, "role": "personel", "ekip": None} for p in OTHER_PERSONEL
]

XP_TARGETS = {p["username"]: p["xp"] for p in MH_PERSONEL}

CURRENT_STATUS_OVERRIDES = {
    "hande.korkmaz": "offline",
    "selin.koc": "offline",
    "gokhan.polat": "mola",
    "burak.yildiz": "cagri_da",
    "elif.sahin": "cagri_da",
    "can.arslan": "mesgul",
}

# ── YARDIMCI FONKSIYONLAR ────────────────────────────────────────────────

def log(msg: str):
    print(f"  → {msg}")


def tz_dt(d: date, t: time) -> datetime:
    return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second, tzinfo=TZ)


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def weighted_choice(weight_map: dict):
    keys = list(weight_map.keys())
    weights = list(weight_map.values())
    return random.choices(keys, weights=weights, k=1)[0]


def unique_phone(existing: set) -> str:
    ops = [
        "530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
        "540", "541", "542", "543", "544", "545", "546", "547", "548", "549",
        "550", "551", "552", "553", "554", "555", "556", "557", "558", "559",
    ]
    for _ in range(10000):
        p = f"0{random.choice(ops)}{random.randint(1000000, 9999999)}"
        if p not in existing:
            existing.add(p)
            return p
    raise RuntimeError("Telefon uretilemedi")


def unique_email(ad: str, soyad: str, existing: set) -> str:
    tbl = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    a = ad.translate(tbl).lower().replace(" ", "")
    s = soyad.translate(tbl).lower().replace(" ", "")
    for _ in range(100):
        e = f"{a}.{s}{random.randint(1,999)}@{random.choice(['gmail.com','hotmail.com','outlook.com','yandex.com'])}"
        if e not in existing:
            existing.add(e)
            return e
    return f"{a}.{s}@gmail.com"


def table_exists(cur, name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
        (name,),
    )
    return cur.fetchone() is not None


def is_open_day(d: date) -> bool:
    if d in HOLIDAYS:
        return False
    if d.weekday() == 6 and d not in SPECIAL_FORCE_OPEN:
        return False
    return True


def day_call_volume(d: date) -> int:
    if not is_open_day(d):
        return 0
    if d in SPECIAL_FORCE_OPEN:
        return random.randint(*CALL_RANGES["campaign"])
    weekday = d.weekday()
    if weekday == 5:
        base = CALL_RANGES["sat"]
    elif weekday == 0:
        base = CALL_RANGES["mon"]
    elif weekday in (1, 2, 3):
        base = CALL_RANGES["tue_thu"]
    else:
        base = CALL_RANGES["fri"]

    mult = SPECIAL_DAYS.get(d, 1.0)
    return int(random.randint(*base) * mult)


def allocate_counts(total: int, weights: list[int]) -> list[int]:
    if total <= 0:
        return [0 for _ in weights]
    total_weight = sum(weights) or 1
    raw = [total * w / total_weight for w in weights]
    counts = [int(v) for v in raw]
    remainder = total - sum(counts)
    if remainder > 0:
        for idx in random.sample(range(len(counts)), k=remainder):
            counts[idx] += 1
    return counts


def pick_segment(shift_start: time, shift_end: time):
    segments = []
    weights = []
    for seg_start, seg_end, weight in SEGMENTS:
        start = max(seg_start, shift_start)
        end = min(seg_end, shift_end)
        if start >= end:
            continue
        minutes = int((datetime.combine(date.min, end) - datetime.combine(date.min, start)).seconds / 60)
        segments.append((start, end))
        weights.append(weight * minutes)
    if not segments:
        return shift_start, shift_end
    return random.choices(segments, weights=weights, k=1)[0]


def sample_time_in_shift(d: date, shift_start: time, shift_end: time) -> datetime:
    seg_start, seg_end = pick_segment(shift_start, shift_end)
    start_dt = tz_dt(d, seg_start)
    end_dt = tz_dt(d, seg_end)
    delta = int((end_dt - start_dt).total_seconds())
    if delta <= 0:
        return start_dt
    offset = random.randint(0, delta)
    return start_dt + timedelta(seconds=offset)


def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end


def count_overlaps(intervals, start, end) -> int:
    return sum(1 for s, e in intervals if overlaps(s, e, start, end))

# ── DB VERI YUKLE ──────────────────────────────────────────────────────────

def load_content():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def db_meta_yukle(cur):
    cur.execute("SELECT id, name FROM roles")
    roles = {r[1]: r[0] for r in cur.fetchall()}

    cur.execute("SELECT id, ad FROM departman")
    departmanlar = {r[1]: r[0] for r in cur.fetchall()}

    cur.execute("SELECT id, ad FROM ekip")
    ekipler = {r[1]: r[0] for r in cur.fetchall()}

    log(f"Roller: {list(roles.keys())}")
    log(f"Departmanlar: {list(departmanlar.keys())}")
    log(f"Ekipler: {list(ekipler.keys())}")
    return roles, departmanlar, ekipler


def temizle(cur):
    log("Mevcut veriler temizleniyor...")
    cur.execute("UPDATE cagri_detay SET ai_ozet_id = NULL WHERE ai_ozet_id IS NOT NULL")

    sira = [
        "sikayet", "kb_oneri", "bildirim", "mesaj", "talimat",
        "ticket", "ajanda", "audit_log", "vardiya_talep",
        "xp_hareketi", "personel_rozet", "quest_ilerleme", "quest", "rozet",
        "csat", "cagri_notu", "ai_ozet", "cagri_detay",
        "mola", "mola_kurali", "vardiya",
        "musteri", "kullanici_tercih", "supervisor_ekip", "personel_ekip",
    ]

    for tbl in sira:
        cur.execute(f"DELETE FROM {tbl}")

    log("Temizleme tamamlandı")


def ensure_users(cur, roles, departmanlar):
    log("Kullanici listesi kontrol ediliyor...")
    usernames = [u["username"] for u in USER_SEEDS]
    cur.execute("SELECT id, username, extension FROM users WHERE username = ANY(%s)", (usernames,))
    existing = {row[1]: (row[0], row[2]) for row in cur.fetchall()}

    insert_rows = []
    update_rows = []
    email_pool = set()
    phone_pool = set()
    hashed = bcrypt.hashpw(SIFRE.encode(), bcrypt.gensalt(rounds=10)).decode()

    for u in USER_SEEDS:
        username = u["username"]
        departman_id = departmanlar.get(u.get("departman")) if u.get("departman") else None
        role_id = roles[u["role"]]
        status = CURRENT_STATUS_OVERRIDES.get(username, "aktif")
        vardiya_bas, vardiya_bit = u["shift"]

        if username not in existing:
            uid = str(uuid.uuid4())
            ad, soyad = (u["name"].split(" ", 1) + [""])[:2]
            email = unique_email(ad, soyad, email_pool)
            phone = unique_phone(phone_pool)
            insert_rows.append((
                uid, username, email, phone, u["name"], hashed,
                role_id, u["extension"], departman_id, True, status,
                0, 1, "bronz", vardiya_bas, vardiya_bit,
                datetime.now(TZ) - timedelta(hours=random.randint(1, 72)),
            ))
            existing[username] = (uid, u["extension"])
        else:
            uid = existing[username][0]
            update_rows.append((
                departman_id, u["extension"], status, True,
                vardiya_bas, vardiya_bit, uid,
            ))

    if insert_rows:
        execute_values(cur, """
            INSERT INTO users (
                id, username, email, phone, display_name, hashed_password,
                role_id, extension, departman_id, is_active, current_status,
                xp, level, tier, vardiya_baslangic, vardiya_bitis, last_login
            ) VALUES %s
        """, insert_rows, page_size=200)

    if update_rows:
        execute_values(cur, """
            UPDATE users SET
                departman_id = data.departman_id,
                extension = data.extension,
                current_status = data.current_status,
                is_active = data.is_active,
                vardiya_baslangic = data.vardiya_baslangic,
                vardiya_bitis = data.vardiya_bitis
            FROM (VALUES %s) AS data(
                departman_id, extension, current_status, is_active,
                vardiya_baslangic, vardiya_bitis, id
            )
            WHERE users.id = data.id::uuid
        """, update_rows, page_size=200)

    user_map = {}
    cur.execute("SELECT id, username, extension, departman_id FROM users WHERE username = ANY(%s)", (usernames,))
    for uid, username, ext, departman_id in cur.fetchall():
        seed = next(u for u in USER_SEEDS if u["username"] == username)
        user_map[username] = {
            "id": uid,
            "role": seed["role"],
            "departman": seed.get("departman"),
            "ekip": seed.get("ekip"),
            "extension": ext or seed["extension"],
            "shift": seed["shift"],
        }

    return user_map


def insert_user_prefs(cur, user_map):
    rows = []
    for info in user_map.values():
        rows.append((
            info["id"],
            Json({"email": True, "push": True}),
            Json({"ringtone": "default"}),
            Json({"theme": "light"}),
        ))
    execute_values(cur, """
        INSERT INTO kullanici_tercih (user_id, bildirim_ayarlari, ses_ayarlari, gorunum_ayarlari)
        VALUES %s ON CONFLICT (user_id) DO NOTHING
    """, rows, page_size=200)


def assign_teams(cur, user_map, ekipler):
    personel_rows = []
    supervisor_rows = []

    for p in MH_PERSONEL:
        user = user_map[p["username"]]
        ekip_id = ekipler.get(p["ekip"])
        if ekip_id:
            personel_rows.append((user["id"], ekip_id, datetime.now(TZ)))

    for s in SUPERVISORS:
        user = user_map[s["username"]]
        ekip_id = ekipler.get(s["ekip"])
        if ekip_id:
            supervisor_rows.append((user["id"], ekip_id, datetime.now(TZ)))

    if personel_rows:
        execute_values(cur, """
            INSERT INTO personel_ekip (personel_id, ekip_id, atama_tarihi)
            VALUES %s ON CONFLICT DO NOTHING
        """, personel_rows, page_size=100)

    if supervisor_rows:
        execute_values(cur, """
            INSERT INTO supervisor_ekip (supervisor_id, ekip_id, atama_tarihi)
            VALUES %s ON CONFLICT DO NOTHING
        """, supervisor_rows, page_size=100)

# ── MUSTERI ───────────────────────────────────────────────────────────────

def generate_customers(content):
    log("Musteriler olusturuluyor...")

    isimler = content["musteri_isimleri"]
    sehirler = content["sehirler"]

    city_weights = {
        "İstanbul": 0.30,
        "Ankara": 0.15,
        "İzmir": 0.12,
        "Bursa": 0.05,
        "Antalya": 0.05,
        "Adana": 0.04,
        "Konya": 0.04,
    }

    existing_phones = set()
    existing_emails = set()

    customers = []
    for _ in range(MUSTERI_SAYISI):
        isim = random.choice(isimler)
        ad = isim["ad"]
        soyad = isim["soyad"]

        r = random.random()
        if r < 0.80:
            tip = "standart"
        elif r < 0.90:
            tip = "yeni"
        elif r < 0.95:
            tip = "vip"
        elif r < 0.99:
            tip = "kurumsal"
        else:
            tip = "kara_liste"

        if tip == "kara_liste":
            kara_liste = True
        else:
            kara_liste = False

        if random.random() < 0.75:
            city = weighted_choice(city_weights)
        else:
            city = random.choice(sehirler)

        email = None
        if random.random() < 0.8:
            email = unique_email(ad, soyad, existing_emails)

        customers.append({
            "id": str(uuid.uuid4()),
            "ad": ad,
            "soyad": soyad,
            "telefon": unique_phone(existing_phones),
            "email": email,
            "musteri_tipi": tip,
            "lokasyon": city,
            "kara_liste_mi": kara_liste,
        })

    return customers


def build_customer_call_pool(customers):
    pool = []
    for c in customers:
        r = random.random()
        if r < 0.60:
            quota = 1
        elif r < 0.85:
            quota = random.randint(2, 3)
        elif r < 0.97:
            quota = random.randint(4, 7)
        else:
            quota = random.randint(8, 12)
        c["call_quota"] = quota
        pool.extend([c["id"]] * quota)

    if len(pool) < TARGET_CALLS:
        ekstra = random.choices(customers, k=TARGET_CALLS - len(pool))
        for c in ekstra:
            pool.append(c["id"])
    elif len(pool) > TARGET_CALLS:
        random.shuffle(pool)
        pool = pool[:TARGET_CALLS]

    random.shuffle(pool)
    return pool

# ── VARDIYA & MOLA ────────────────────────────────────────────────────────

def generate_leave_days():
    leave = {}
    all_days = [d for d in daterange(BASLANGIC, BITIS) if d.weekday() < 5]

    for p in MH_PERSONEL:
        username = p["username"]
        if username == "hande.korkmaz":
            last_week = [BITIS - timedelta(days=i) for i in range(7)]
            leave[username] = set(last_week)
        else:
            k = random.randint(3, 5)
            leave[username] = set(random.sample(all_days, k=k))
    return leave


def schedule_breaks_for_person(d: date, shift_start: time, shift_end: time, team_breaks, supervisor_id):
    breaks = []

    def pick_break(window_start: time, window_end: time, duration_min: int, duration_max: int, tur: str):
        for _ in range(50):
            start_dt = tz_dt(d, window_start) + timedelta(minutes=random.randint(0, max(0, int((datetime.combine(date.min, window_end) - datetime.combine(date.min, window_start)).seconds / 60) - duration_min)))
            duration = random.randint(duration_min, duration_max)
            end_dt = start_dt + timedelta(minutes=duration)
            if end_dt.time() > shift_end:
                continue
            if count_overlaps(team_breaks, start_dt, end_dt) >= 2:
                continue
            team_breaks.append((start_dt, end_dt))
            breaks.append((start_dt, end_dt, duration, tur))
            return

    lunch_start = max(time(12, 0), shift_start)
    lunch_end = min(time(13, 30), shift_end)
    if lunch_start < lunch_end:
        pick_break(lunch_start, lunch_end, 30, 45, "yemek")

    short_breaks = random.randint(1, 2)
    for _ in range(short_breaks):
        window_start = max(time(10, 0), shift_start)
        window_end = min(time(17, 30), shift_end)
        pick_break(window_start, window_end, 15, 20, "kisisel")

    mola_rows = []
    for bas, bit, sure, tur in breaks:
        r = random.random()
        if r < 0.95:
            durum = "tamamlandi"
        elif r < 0.98:
            durum = "reddedildi"
        else:
            durum = "beklemede"

        mola_rows.append({
            "baslangic": bas,
            "bitis": bit,
            "planlanan_bitis": bit,
            "tur": tur,
            "sure_dakika": sure,
            "durum": durum,
            "supervisor_id": supervisor_id if durum != "beklemede" else None,
            "supervisor_notu": "" if durum != "reddedildi" else "Yoğunluk nedeni ile reddedildi",
        })

    return mola_rows

# ── CAGRI URETIMI ─────────────────────────────────────────────────────────

def build_daily_targets():
    targets = {}
    for d in daterange(BASLANGIC, BITIS):
        targets[d] = day_call_volume(d)
    return targets


def pick_outcome():
    return weighted_choice(CALL_RESULT_WEIGHTS)


def pick_category():
    return weighted_choice(CATEGORY_WEIGHTS)


def generate_calls_for_person_day(
    person,
    d: date,
    call_count: int,
    shift_start: time,
    shift_end: time,
    breaks,
    customers_by_id,
    call_pool,
    all_extensions,
):
    calls = []
    if call_count <= 0:
        return calls

    planned_times = [sample_time_in_shift(d, shift_start, shift_end) for _ in range(call_count)]
    planned_times.sort()

    break_intervals = [(b["baslangic"], b["bitis"]) for b in breaks]
    prev_end = tz_dt(d, shift_start)

    for base_time in planned_times:
        direction = weighted_choice(CALL_DIRECTION_WEIGHTS)
        category = pick_category()
        outcome = pick_outcome()

        duration = random.randint(*CATEGORY_DURATION[category])
        if outcome in ("cevaplanmadi", "mesgul"):
            duration = random.randint(10, 35)
        elif outcome == "aktarildi":
            duration += random.randint(120, 300)

        wait_time = random.randint(15, 90)

        start_time = max(base_time, prev_end + timedelta(seconds=random.randint(5, 45)))
        for b_start, b_end in break_intervals:
            if overlaps(start_time, start_time + timedelta(seconds=duration), b_start, b_end):
                start_time = b_end + timedelta(seconds=random.randint(5, 30))

        end_time = start_time + timedelta(seconds=duration)
        if end_time.time() > shift_end:
            continue

        prev_end = end_time

        call_center_no = "0232 442 07 07"
        customer = None
        arayan_no = call_center_no
        aranan_no = call_center_no

        if direction != "dahili":
            customer_id = call_pool.pop() if call_pool else random.choice(list(customers_by_id.keys()))
            customer = customers_by_id.get(customer_id)
            if not customer:
                continue
            arayan_no = customer["telefon"]
            aranan_no = call_center_no

        if direction == "giden":
            arayan_no = person["extension"]
            aranan_no = customer["telefon"]
        elif direction == "dahili":
            arayan_no = person["extension"]
            aranan_no = random.choice(all_extensions)

        transfer = outcome == "aktarildi"
        aktarilan = None
        if transfer:
            aktarilan = weighted_choice(TRANSFER_DEPT_WEIGHTS)

        ivr_map = {
            "bilgi": "1-1",
            "satis": "1-2",
            "sikayet": "1-3",
            "teknik": "2",
            "diger": "0",
        }

        calls.append({
            "id": str(uuid.uuid4()),
            "cdr_uniqueid": f"sporthink-{random.randint(10000000, 99999999)}",
            "personel_id": person["id"],
            "musteri_id": customer["id"] if customer else None,
            "arayan_no": arayan_no,
            "aranan_no": aranan_no,
            "cagri_yonu": direction,
            "kuyruk_adi": "queue_mh",
            "ivr_yolu": ivr_map.get(category, "0"),
            "dahili_no": person["extension"],
            "baslangic_zamani": start_time,
            "bitis_zamani": end_time,
            "sure_saniye": duration,
            "bekleme_suresi_saniye": wait_time,
            "kategori": category,
            "cagri_sonucu": outcome,
            "aktarim_yapildi_mi": transfer,
            "aktarilan_departman": aktarilan,
            "aktaran_personel_id": person["id"] if transfer else None,
            "aktarim_nedeni": "Birim uzmanligi gerektigi icin aktarildi" if transfer else None,
            "ai_ozet_id": None,
            "ai_ozet_onaylandi": None,
            "ses_kaydi_url": None,
            "ses_kaydi_sure": None,
            "csat_skoru": None,
            "olusturma_tarihi": start_time,
            "musteri": customer,
        })

    return calls

# ── EK VERI SETLERI ───────────────────────────────────────────────────────

def generate_notes(content, calls):
    note_templates = {
        "bilgi": [
            "Stok durumu kontrol edildi, {URUN} icin 3 gun icinde tedarik saglanacak.",
            "Mağaza calisma saatleri paylasildi, {SEHIR} subesi icin bilgi verildi.",
        ],
        "satis": [
            "Siparis no {SIPARIS} icin kargo durumu guncellendi, takip linki gonderildi.",
            "Kampanya kodu kullanimi aciklandi, musteriye email iletildi.",
        ],
        "sikayet": [
            "Gec teslimat icin ozur iletildi, iade proseduru anlatildi.",
            "Hasarli urun fotograflari istendi, surec acildi.",
        ],
        "teknik": [
            "Uygulama girisi icin sifre sifirlama yapildi.",
            "Odeme sayfasi hatasi kayit altina alindi, IT ekibine iletildi.",
        ],
        "diger": [
            "Uyelik bilgileri guncellendi, KVKK metni paylasildi.",
            "Musteri geri arama istedi, ajandaya eklendi.",
        ],
    }

    pool = content.get("sporthink_urunleri", [])
    sehirler = content.get("sehirler", ["Istanbul"])

    notes = []
    for call in calls:
        if call.get("musteri_id") is None:
            continue
        if random.random() > 0.60:
            continue
        template_list = note_templates.get(call["kategori"], note_templates["diger"])
        template = random.choice(template_list)
        text = (
            template
            .replace("{URUN}", random.choice(pool))
            .replace("{SEHIR}", random.choice(sehirler))
            .replace("{SIPARIS}", f"{call['baslangic_zamani'].year}{random.randint(100000,999999)}")
        )
        notes.append({
            "id": str(uuid.uuid4()),
            "cagri_id": call["id"],
            "musteri_id": call["musteri_id"],
            "personel_id": call["personel_id"],
            "icerik": text,
            "kategori": call["kategori"],
            "etiketler": [call["kategori"], "musteri"],
            "oncelik": random.choice(["dusuk", "orta", "yuksek"]),
            "olusturma_tarihi": call["baslangic_zamani"],
        })
    return notes


def generate_csat(calls):
    csat_rows = []
    for call in calls:
        if call.get("musteri_id") is None:
            continue
        if call["cagri_sonucu"] != "cevaplandi":
            continue
        skor = weighted_choice(CSAT_WEIGHTS)
        call["csat_skoru"] = skor
        csat_rows.append({
            "id": str(uuid.uuid4()),
            "cagri_id": call["id"],
            "musteri_id": call["musteri_id"],
            "personel_id": call["personel_id"],
            "skor": skor,
            "yorum": None,
            "olusturma_tarihi": call["baslangic_zamani"] + timedelta(minutes=random.randint(5, 30)),
        })
    return csat_rows


def generate_complaints(calls, supervisors, admin_id):
    sikayet_calls = [c for c in calls if c["kategori"] == "sikayet" and c.get("musteri_id") is not None]
    random.shuffle(sikayet_calls)
    target = min(len(sikayet_calls), random.randint(150, 180))
    selected = sikayet_calls[:target]

    complaints = []
    for call in selected:
        r = random.random()
        if r < 0.70:
            durum = "onaylandi"
        elif r < 0.90:
            durum = "reddedildi"
        elif r < 0.95:
            durum = "olusturuldu"
        else:
            durum = "admin_iptali"

        supervisor_id = random.choice(supervisors) if durum in ("onaylandi", "reddedildi", "admin_iptali") else None
        admin_ref = admin_id if durum == "admin_iptali" else None

        complaints.append({
            "id": str(uuid.uuid4()),
            "personel_id": call["personel_id"],
            "musteri_id": call["musteri_id"],
            "musteri_telefon": call["musteri"]["telefon"],
            "cagri_id": call["id"],
            "kategori": random.choice(["davranis", "urun", "kargo", "iade", "teknik", "diger"]),
            "aciklama": "Musteri memnuniyetsizligi kayda alindi.",
            "durum": durum,
            "supervisor_id": supervisor_id,
            "supervisor_notu": "Inceleme tamamlandi" if supervisor_id else None,
            "supervisor_tarih": call["baslangic_zamani"] + timedelta(days=random.randint(0, 3)) if supervisor_id else None,
            "admin_id": admin_ref,
            "admin_notu": "Admin iptali" if admin_ref else None,
            "admin_tarih": call["baslangic_zamani"] + timedelta(days=random.randint(1, 5)) if admin_ref else None,
            "xp_dusuldu_mu": durum == "onaylandi",
            "xp_geri_yuklendi_mi": durum == "admin_iptali",
            "created_at": call["baslangic_zamani"],
        })

    return complaints


def generate_tickets(user_ids):
    rows = []
    for _ in range(random.randint(30, 40)):
        user_id = random.choice(user_ids)
        status = random.choices(TICKET_STATUS, weights=[0.25, 0.25, 0.50])[0]
        created_at = tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(random.randint(9, 18), random.randint(0, 59)))
        yanit = "Sorun cozuldu, cihaz degistirildi" if status == "resolved" else None
        yanit_tarihi = created_at + timedelta(days=random.randint(1, 5)) if status == "resolved" else None
        rows.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "kategori": random.choices(TICKET_CATS, weights=TICKET_CAT_WEIGHTS, k=1)[0],
            "baslik": "IT destek talebi",
            "aciklama": "Sistem erisim sorunu yasaniyor.",
            "ekran_goruntu_url": None,
            "durum": status,
            "oncelik": random.choice(TICKET_PRIORITY),
            "atanan_id": None,
            "yanit": yanit,
            "yanit_tarihi": yanit_tarihi,
            "created_at": created_at,
        })
    return rows


def generate_vardiya_talepleri(personel_ids, supervisors, admin_id):
    rows = []
    for _ in range(random.randint(25, 35)):
        personel_id = random.choice(personel_ids)
        hedef_tarih = random.choice([d for d in daterange(BASLANGIC, BITIS) if d.weekday() in (0, 1)])
        durum = random.choices(["onaylandi", "reddedildi", "supervisor_gorus", "gonderildi"], weights=[0.50, 0.25, 0.15, 0.10])[0]
        supervisor_id = random.choice(supervisors) if durum in ("onaylandi", "reddedildi", "supervisor_gorus") else None
        admin_id_val = admin_id if durum in ("onaylandi", "reddedildi") else None

        rows.append({
            "id": str(uuid.uuid4()),
            "talep_eden_id": personel_id,
            "hedef_personel_id": personel_id,
            "hedef_tarih": hedef_tarih,
            "mevcut_baslangic": time(9, 0),
            "mevcut_bitis": time(18, 0),
            "talep_baslangic": time(10, 0),
            "talep_bitis": time(19, 0),
            "gerekce": "Kisisel isler nedeniyle vardiya degisimi talep edildi.",
            "supervisor_gorusu": "uygun" if durum in ("onaylandi", "supervisor_gorus") else None,
            "supervisor_notu": "Uygun" if supervisor_id else None,
            "supervisor_id": supervisor_id,
            "supervisor_tarih": tz_dt(hedef_tarih, time(11, 0)) if supervisor_id else None,
            "durum": durum,
            "admin_notu": "Onaylandi" if admin_id_val else None,
            "admin_id": admin_id_val,
            "admin_tarih": tz_dt(hedef_tarih, time(12, 0)) if admin_id_val else None,
            "created_at": tz_dt(hedef_tarih - timedelta(days=random.randint(1, 7)), time(9, 30)),
        })
    return rows


def generate_messages(user_ids):
    rows = []
    total = random.randint(500, 800)
    for _ in range(total):
        sender, receiver = random.sample(user_ids, 2)
        created_at = tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(random.randint(9, 18), random.randint(0, 59)))
        okundu = random.random() < 0.8
        rows.append({
            "id": str(uuid.uuid4()),
            "gonderen_id": sender,
            "alici_id": receiver,
            "icerik": "Toplantı notu paylaşıldı.",
            "okundu": okundu,
            "okundu_tarihi": created_at + timedelta(minutes=random.randint(1, 180)) if okundu else None,
            "olusturma_tarihi": created_at,
        })
    return rows


def generate_notifications(user_ids):
    rows = []
    for uid in user_ids:
        count = random.randint(20, 40)
        for _ in range(count):
            created_at = tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(random.randint(8, 19), random.randint(0, 59)))
            okundu = random.random() < 0.8
            rows.append({
                "id": str(uuid.uuid4()),
                "alici_id": uid,
                "tip": random.choice(["cagri", "sistem", "kampanya", "uyari"]),
                "baslik": "Bilgilendirme",
                "icerik": "Yeni kampanya bilgilendirmesi paylasildi.",
                "okundu": okundu,
                "referans_tip": None,
                "referans_id": None,
                "olusturma_tarihi": created_at,
            })
    return rows


def generate_talimat(admin_id, ekipler, supervisors):
    rows = []
    for _ in range(random.randint(15, 20)):
        created_at = tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(random.randint(9, 18), random.randint(0, 59)))
        ekip_id = random.choice(list(ekipler.values())) if ekipler else None
        okundu = random.random() < 0.7
        rows.append({
            "id": str(uuid.uuid4()),
            "gonderen_id": admin_id,
            "alici_ekip_id": ekip_id,
            "alici_user_id": random.choice(supervisors) if random.random() < 0.4 else None,
            "baslik": "Kampanya bilgilendirmesi",
            "icerik": "Yeni kampanya icin CSAT hedefi guncellendi.",
            "oncelik": random.choice(["dusuk", "orta", "yuksek"]),
            "okundu": okundu,
            "okundu_tarihi": created_at + timedelta(hours=random.randint(1, 24)) if okundu else None,
            "uygulanma_durumu": random.choice(["beklemede", "tamamlandi"]),
            "itiraz_metni": None,
            "itiraz_tarihi": None,
            "olusturma_tarihi": created_at,
        })
    return rows


def generate_quest_and_progress(personel_ids, ekipler, admin_id):
    quest_rows = []
    progress_rows = []

    quest_defs = [
        ("Gunluk 40 cagri", "cagri", 40, 30, "gunluk"),
        ("CSAT 4.5 ustu", "csat", 45, 50, "haftalik"),
        ("Haftalik 200 cagri", "cagri", 200, 45, "haftalik"),
        ("Sifir cevapsiz", "cevapsiz", 0, 40, "gunluk"),
        ("AI ozet onayi", "ai", 10, 25, "gunluk"),
    ]

    max_k = min(8, len(quest_defs))
    for title, metric, target, reward, scope in random.sample(quest_defs, k=random.randint(5, max_k)):
        qid = str(uuid.uuid4())
        quest_rows.append({
            "id": qid,
            "baslik": title,
            "aciklama": title,
            "hedef_deger": target,
            "odul_xp": reward,
            "odul_rozet_id": None,
            "zorluk": random.choice(["kolay", "orta", "zor"]),
            "kapsam": scope,
            "metrik": metric,
            "hedef_ekip_id": random.choice(list(ekipler.values())) if ekipler else None,
            "bitis_tarihi": BITIS,
            "olusturan_id": admin_id,
            "aktif": True,
            "olusturma_tarihi": tz_dt(BASLANGIC, time(9, 0)),
        })

        for pid in random.sample(personel_ids, k=min(len(personel_ids), random.randint(8, 10))):
            progress = random.randint(0, target + 10)
            durum = "tamamlandi" if progress >= target else "aktif"
            progress_rows.append({
                "id": str(uuid.uuid4()),
                "quest_id": qid,
                "personel_id": pid,
                "mevcut_deger": progress,
                "durum": durum,
                "tamamlandi_at": tz_dt(BITIS, time(12, 0)) if durum == "tamamlandi" else None,
                "olusturma_tarihi": tz_dt(BASLANGIC, time(9, 0)),
            })

    return quest_rows, progress_rows


def generate_rozetler():
    names = [
        "Ilk Cagri", "100 Cagri", "500 Cagri", "CSAT Ustasi", "Hizli Cozum",
        "Takim Lideri", "Kampanya Yildizi", "Musteri Dostu", "Disiplin",
        "Yuksek Performans", "Haftanin Yildizi", "Ayin Yildizi",
    ]
    rows = []
    for ad in names:
        rows.append({
            "id": str(uuid.uuid4()),
            "ad": ad,
            "aciklama": ad,
            "ikon_url": None,
            "kategori": "genel",
            "nadirlik": random.choice(["bronz", "gumus", "altin", "platin"]),
            "kosul_tipi": "kural",
            "kosul_deger": Json({"value": random.randint(1, 500)}),
            "kosul_aciklama": ad,
            "aktif": True,
            "olusturma_tarihi": tz_dt(BASLANGIC, time(9, 0)),
        })
    return rows


def generate_kb(content, admin_id, personel_ids):
    makaleler = []
    mevcut = content.get("kb_makaleleri", [])
    for m in mevcut:
        makaleler.append({
            "id": str(uuid.uuid4()),
            "baslik": m["baslik"],
            "icerik": m["icerik"],
            "kategori": m.get("kategori"),
            "alt_kategori": m.get("alt_kategori"),
            "etiketler": m.get("etiketler", []),
            "yazar_id": admin_id,
            "aktif": True,
            "goruntuleme": random.randint(30, 300),
            "faydali_oy": random.randint(5, 120),
            "faydasiz_oy": random.randint(0, 30),
            "olusturma_tarihi": tz_dt(BASLANGIC, time(9, 0)),
            "guncelleme_tarihi": tz_dt(BITIS, time(12, 0)),
        })

    for i in range(40):
        makaleler.append({
            "id": str(uuid.uuid4()),
            "baslik": f"SSS Makale {i+1}",
            "icerik": "Sik sorulan sorulara yanitlar.",
            "kategori": random.choice(["siparis", "kargo", "iade", "uygulama"]),
            "alt_kategori": None,
            "etiketler": ["sss"],
            "yazar_id": admin_id,
            "aktif": True,
            "goruntuleme": random.randint(20, 400),
            "faydali_oy": random.randint(2, 80),
            "faydasiz_oy": random.randint(0, 20),
            "olusturma_tarihi": tz_dt(BASLANGIC, time(9, 0)),
            "guncelleme_tarihi": tz_dt(BITIS, time(12, 0)),
        })

    oneriler = []
    for _ in range(10):
        personel_id = random.choice(personel_ids)
        oneriler.append({
            "id": str(uuid.uuid4()),
            "personel_id": personel_id,
            "baslik": "KB Onerisi",
            "icerik": "Musteri sik sorulari icin yeni madde onerisi.",
            "onaylanan_icerik": None,
            "kategori": random.choice(["siparis", "kargo", "iade", "uygulama"]),
            "durum": random.choice(["beklemede", "onaylandi", "reddedildi", "admin_iptali"]),
            "supervisor_id": None,
            "supervisor_notu": None,
            "created_at": tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(11, 0)),
        })

    return makaleler, oneriler


def generate_ajanda(personel_ids, customers):
    rows = []
    for _ in range(random.randint(50, 80)):
        user_id = random.choice(personel_ids)
        musteri = random.choice(customers)
        d = random.choice(list(daterange(BASLANGIC, BITIS)))
        rows.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "musteri_id": musteri["id"],
            "tarih": d,
            "saat": time(random.randint(9, 18), random.randint(0, 59)),
            "baslik": "Geri arama",
            "aciklama": "Musteri geri arama talebi.",
            "tip": "geri_arama",
            "oncelik": random.choice(["dusuk", "orta", "yuksek"]),
            "durum": random.choice(["tamamlandi", "beklemede"]),
            "tekrar": "yok",
            "olusturma_tarihi": tz_dt(d, time(9, 0)),
        })
    return rows


def generate_audit(admin_id):
    rows = []
    for _ in range(random.randint(30, 50)):
        created_at = tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(random.randint(9, 18), random.randint(0, 59)))
        rows.append({
            "id": str(uuid.uuid4()),
            "user_id": admin_id,
            "eylem": random.choice(["USER_UPDATE", "BREAK_DECIDE", "QUEST_CREATE", "ROLE_CHANGE"]),
            "hedef_tip": "users",
            "hedef_id": None,
            "detay": Json({"note": "admin aksiyonu"}),
            "ip_adresi": "127.0.0.1",
            "created_at": created_at,
        })
    return rows

# ── MAIN ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Sporthink Cagri Merkezi — 90 Gunluk Seed (Senaryo)")
    print(f"Aralik: {BASLANGIC} -> {BITIS}")
    print("=" * 70)

    print("\n[1] JSON icerik yukleniyor...")
    content = load_content()

    print("\n[2] PostgreSQL baglantisi...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("\n[3] Meta veriler...")
        roles, departmanlar, ekipler = db_meta_yukle(cur)

        print("\n[4] Tablolar temizleniyor...")
        temizle(cur)

        print("\n[5] Kullanici kontrolu...")
        user_map = ensure_users(cur, roles, departmanlar)
        insert_user_prefs(cur, user_map)
        assign_teams(cur, user_map, ekipler)

        admin_id = user_map[ADMIN_USERS[0]["username"]]["id"]
        supervisor_ids = [user_map[s["username"]]["id"] for s in SUPERVISORS]
        mh_ids = [user_map[p["username"]]["id"] for p in MH_PERSONEL]
        all_user_ids = [u["id"] for u in user_map.values()]
        all_extensions = [u["extension"] for u in user_map.values() if u.get("extension")]

        print("\n[6] Musteriler olusturuluyor...")
        customers = generate_customers(content)
        customer_by_id = {c["id"]: c for c in customers}
        call_pool = build_customer_call_pool(customers)

        customer_rows = [(
            c["id"], c["ad"], c["soyad"], c["telefon"], c["email"],
            c["musteri_tipi"], c["lokasyon"], "manuel", None, None, None, c["kara_liste_mi"],
            None, admin_id, tz_dt(BASLANGIC, time(9, 0)), tz_dt(BITIS, time(18, 0)),
        ) for c in customers]

        execute_values(cur, """
            INSERT INTO musteri (
                id, ad, soyad, telefon, email, musteri_tipi, lokasyon, kaynak,
                dis_sistem_id, toplam_cagri_sayisi, ortalama_csat_skoru, kara_liste_mi,
                son_arama_zamani, olusturan_id, olusturma_tarihi, guncelleme_tarihi
            ) VALUES %s
        """, customer_rows, page_size=500)

        print("\n[7] Vardiya & mola...")
        leave_days = generate_leave_days()
        vardiya_rows = []
        mola_rows = []
        breaks_by_person = {}
        team_breaks_by_day = {}

        saturday_rotation = [p["username"] for p in MH_PERSONEL]
        sat_index = 0

        for d in daterange(BASLANGIC, BITIS):
            if not is_open_day(d):
                continue

            is_saturday = d.weekday() == 5 and d not in SPECIAL_FORCE_OPEN
            saturday_staff = []
            if is_saturday:
                available = [u for u in saturday_rotation if d not in leave_days.get(u, set())]
                if len(available) < 2:
                    available = saturday_rotation
                saturday_staff = [available[sat_index % len(available)], available[(sat_index + 1) % len(available)]]
                sat_index += 2

            for u in USER_SEEDS:
                username = u["username"]
                info = user_map[username]
                if info["role"] == "admin":
                    continue

                if info["role"] == "personel" and u.get("ekip") == "MH Ekip A" or u.get("ekip") == "MH Ekip B":
                    if d in leave_days.get(username, set()):
                        continue
                    if is_saturday and username not in saturday_staff:
                        continue

                if d.weekday() >= 5 and info["role"] != "personel":
                    continue

                shift_start, shift_end = info["shift"]
                if is_saturday:
                    shift_start, shift_end = time(9, 0), time(14, 0)

                vardiya_rows.append((
                    str(uuid.uuid4()), info["id"], d, "normal",
                    shift_start, shift_end, admin_id,
                    tz_dt(d, shift_start),
                ))

                if info["role"] != "personel":
                    continue

                ekip = info.get("ekip") or "genel"
                team_breaks = team_breaks_by_day.setdefault((ekip, d), [])
                mola_entries = schedule_breaks_for_person(d, shift_start, shift_end, team_breaks, random.choice(supervisor_ids) if supervisor_ids else None)
                breaks_by_person[(info["id"], d)] = mola_entries

                for m in mola_entries:
                    mola_rows.append((
                        str(uuid.uuid4()), info["id"], m["baslangic"], m["bitis"], m["planlanan_bitis"],
                        m["tur"], m["sure_dakika"], m["durum"], m["supervisor_id"], m["supervisor_notu"],
                        m["baslangic"],
                    ))

        if vardiya_rows:
            execute_values(cur, """
                INSERT INTO vardiya (id, personel_id, tarih, tip, baslangic, bitis, olusturan_id, olusturma_tarihi)
                VALUES %s
            """, vardiya_rows, page_size=500)

        if mola_rows:
            execute_values(cur, """
                INSERT INTO mola (id, personel_id, baslangic, bitis, planlanan_bitis, tur,
                    sure_dakika, durum, supervisor_id, supervisor_notu, created_at)
                VALUES %s
            """, mola_rows, page_size=500)

        print("\n[8] Cagrilar uretliyor...")
        daily_targets = build_daily_targets()

        calls = []
        for d, total_calls in daily_targets.items():
            if total_calls <= 0:
                continue

            is_saturday = d.weekday() == 5 and d not in SPECIAL_FORCE_OPEN
            staff = []
            weights = []
            for p in MH_PERSONEL:
                username = p["username"]
                if d in leave_days.get(username, set()):
                    continue
                if is_saturday:
                    # only 2 staff on Saturday
                    continue
                staff.append(username)
                weights.append(p["xp"])

            if is_saturday:
                saturday_staff = [p["username"] for p in MH_PERSONEL if d not in leave_days.get(p["username"], set())]
                if len(saturday_staff) >= 2:
                    staff = random.sample(saturday_staff, k=2)
                    weights = [XP_TARGETS[s] for s in staff]

            if not staff:
                continue

            counts = allocate_counts(total_calls, weights)

            for username, count in zip(staff, counts):
                info = user_map[username]
                shift_start, shift_end = info["shift"]
                if is_saturday:
                    shift_start, shift_end = time(9, 0), time(14, 0)

                breaks = breaks_by_person.get((info["id"], d), [])
                calls.extend(generate_calls_for_person_day(
                    info, d, count, shift_start, shift_end,
                    breaks, customer_by_id, call_pool, all_extensions,
                ))

        print(f"    {len(calls)} cagri olustu")

        call_rows = [(
            c["id"], c["cdr_uniqueid"], c["personel_id"], c["musteri_id"],
            c["arayan_no"], c["aranan_no"], c["cagri_yonu"], c["kuyruk_adi"],
            c["ivr_yolu"], c["dahili_no"], c["baslangic_zamani"], c["bitis_zamani"],
            c["sure_saniye"], c["bekleme_suresi_saniye"], c["kategori"], c["cagri_sonucu"],
            c["aktarim_yapildi_mi"], c["aktarilan_departman"], c["aktaran_personel_id"],
            c["aktarim_nedeni"], c["ai_ozet_id"], c["ai_ozet_onaylandi"],
            c["ses_kaydi_url"], c["ses_kaydi_sure"], c["csat_skoru"], c["olusturma_tarihi"],
        ) for c in calls]

        execute_values(cur, """
            INSERT INTO cagri_detay (
                id, cdr_uniqueid, personel_id, musteri_id, arayan_no, aranan_no,
                cagri_yonu, kuyruk_adi, ivr_yolu, dahili_no,
                baslangic_zamani, bitis_zamani, sure_saniye, bekleme_suresi_saniye,
                kategori, cagri_sonucu, aktarim_yapildi_mi, aktarilan_departman,
                aktaran_personel_id, aktarim_nedeni, ai_ozet_id, ai_ozet_onaylandi,
                ses_kaydi_url, ses_kaydi_sure, csat_skoru, olusturma_tarihi
            ) VALUES %s
        """, call_rows, page_size=500)

        print("\n[9] Notlar & CSAT...")
        notes = generate_notes(content, calls)
        csat_rows = generate_csat(calls)

        if notes:
            execute_values(cur, """
                INSERT INTO cagri_notu (id, cagri_id, musteri_id, personel_id,
                    icerik, kategori, etiketler, oncelik, olusturma_tarihi)
                VALUES %s
            """, [(
                n["id"], n["cagri_id"], n["musteri_id"], n["personel_id"], n["icerik"],
                n["kategori"], n["etiketler"], n["oncelik"], n["olusturma_tarihi"],
            ) for n in notes], page_size=500)

        if csat_rows:
            execute_values(cur, """
                INSERT INTO csat (id, cagri_id, musteri_id, personel_id, skor, yorum, olusturma_tarihi)
                VALUES %s
            """, [(
                c["id"], c["cagri_id"], c["musteri_id"], c["personel_id"], c["skor"],
                c["yorum"], c["olusturma_tarihi"],
            ) for c in csat_rows], page_size=500)

        print("\n[10] Sikayetler...")
        complaints = generate_complaints(calls, supervisor_ids, admin_id)
        if complaints:
            execute_values(cur, """
                INSERT INTO sikayet (
                    id, personel_id, musteri_id, musteri_telefon, cagri_id, kategori,
                    aciklama, durum, supervisor_id, supervisor_notu, supervisor_tarih,
                    admin_id, admin_notu, admin_tarih, xp_dusuldu_mu, xp_geri_yuklendi_mi, created_at
                ) VALUES %s
            """, [(
                s["id"], s["personel_id"], s["musteri_id"], s["musteri_telefon"], s["cagri_id"], s["kategori"],
                s["aciklama"], s["durum"], s["supervisor_id"], s["supervisor_notu"], s["supervisor_tarih"],
                s["admin_id"], s["admin_notu"], s["admin_tarih"], s["xp_dusuldu_mu"], s["xp_geri_yuklendi_mi"], s["created_at"],
            ) for s in complaints], page_size=300)

        print("\n[11] XP hareketleri...")
        xp_rows = []
        xp_totals = {pid: 0 for pid in mh_ids}
        for call in calls:
            if call["cagri_sonucu"] not in ("cevaplandi", "aktarildi"):
                continue
            pid = call["personel_id"]
            if pid not in xp_totals:
                continue
            xp_rows.append((
                str(uuid.uuid4()), pid, 10, "Cagri tamamlama", call["id"], "cagri", None, call["baslangic_zamani"],
            ))
            xp_totals[pid] += 10

            if call["csat_skoru"] == 5:
                xp_rows.append((
                    str(uuid.uuid4()), pid, 5, "CSAT 5 bonus", call["id"], "cagri", None, call["baslangic_zamani"],
                ))
                xp_totals[pid] += 5
            elif call["csat_skoru"] == 4:
                xp_rows.append((
                    str(uuid.uuid4()), pid, 3, "CSAT 4 bonus", call["id"], "cagri", None, call["baslangic_zamani"],
                ))
                xp_totals[pid] += 3

        for s in complaints:
            if s["xp_dusuldu_mu"]:
                xp_rows.append((
                    str(uuid.uuid4()), s["personel_id"], -20, "Onayli sikayet", s["id"], "sikayet", None, s["created_at"],
                ))
                if s["personel_id"] in xp_totals:
                    xp_totals[s["personel_id"]] -= 20
            if s["xp_geri_yuklendi_mi"]:
                xp_rows.append((
                    str(uuid.uuid4()), s["personel_id"], 20, "Sikayet iptali", s["id"], "sikayet", None, s["created_at"],
                ))
                if s["personel_id"] in xp_totals:
                    xp_totals[s["personel_id"]] += 20

        # Quest odulleri
        quest_rows, progress_rows = generate_quest_and_progress(mh_ids, ekipler, admin_id)
        for p in progress_rows:
            if p["durum"] == "tamamlandi":
                reward = next(q["odul_xp"] for q in quest_rows if q["id"] == p["quest_id"])
                xp_rows.append((
                    str(uuid.uuid4()), p["personel_id"], reward, "Quest tamamlandi", p["quest_id"], "quest", None, p["tamamlandi_at"],
                ))
                xp_totals[p["personel_id"]] = xp_totals.get(p["personel_id"], 0) + reward

        # XP hedeflerine yaklas
        for username, target in XP_TARGETS.items():
            pid = user_map[username]["id"]
            current = xp_totals.get(pid, 0)
            diff = target - current
            if diff != 0:
                xp_rows.append((
                    str(uuid.uuid4()), pid, diff, "Manuel duzeltme", None, "manuel", admin_id, tz_dt(BITIS, time(15, 0)),
                ))
                xp_totals[pid] = target

        if xp_rows:
            execute_values(cur, """
                INSERT INTO xp_hareketi (id, personel_id, miktar, sebep, referans_id, referans_tip, duzelten_id, olusturma_tarihi)
                VALUES %s
            """, xp_rows, page_size=500)

        print("\n[12] Diger tablolar...")
        tickets = generate_tickets(mh_ids)
        if tickets:
            execute_values(cur, """
                INSERT INTO ticket (id, user_id, kategori, baslik, aciklama, ekran_goruntu_url,
                    durum, oncelik, atanan_id, yanit, yanit_tarihi, created_at)
                VALUES %s
            """, [(
                t["id"], t["user_id"], t["kategori"], t["baslik"], t["aciklama"], t["ekran_goruntu_url"],
                t["durum"], t["oncelik"], t["atanan_id"], t["yanit"], t["yanit_tarihi"], t["created_at"],
            ) for t in tickets], page_size=200)

        vardiya_talep_rows = generate_vardiya_talepleri(mh_ids, supervisor_ids, admin_id)
        if vardiya_talep_rows:
            execute_values(cur, """
                INSERT INTO vardiya_talep (
                    id, talep_eden_id, hedef_personel_id, hedef_tarih, mevcut_baslangic, mevcut_bitis,
                    talep_baslangic, talep_bitis, gerekce, supervisor_gorusu, supervisor_notu, supervisor_id,
                    supervisor_tarih, durum, admin_notu, admin_id, admin_tarih, created_at
                ) VALUES %s
            """, [(
                v["id"], v["talep_eden_id"], v["hedef_personel_id"], v["hedef_tarih"], v["mevcut_baslangic"], v["mevcut_bitis"],
                v["talep_baslangic"], v["talep_bitis"], v["gerekce"], v["supervisor_gorusu"], v["supervisor_notu"], v["supervisor_id"],
                v["supervisor_tarih"], v["durum"], v["admin_notu"], v["admin_id"], v["admin_tarih"], v["created_at"],
            ) for v in vardiya_talep_rows], page_size=200)

        messages = generate_messages(all_user_ids)
        if messages:
            execute_values(cur, """
                INSERT INTO mesaj (id, gonderen_id, alici_id, icerik, okundu, okundu_tarihi, olusturma_tarihi)
                VALUES %s
            """, [(
                m["id"], m["gonderen_id"], m["alici_id"], m["icerik"], m["okundu"], m["okundu_tarihi"], m["olusturma_tarihi"],
            ) for m in messages], page_size=500)

        notifications = generate_notifications(all_user_ids)
        if notifications:
            execute_values(cur, """
                INSERT INTO bildirim (id, alici_id, tip, baslik, icerik, okundu, referans_tip, referans_id, olusturma_tarihi)
                VALUES %s
            """, [(
                n["id"], n["alici_id"], n["tip"], n["baslik"], n["icerik"], n["okundu"], n["referans_tip"], n["referans_id"], n["olusturma_tarihi"],
            ) for n in notifications], page_size=500)

        talimat_rows = generate_talimat(admin_id, ekipler, supervisor_ids)
        if talimat_rows:
            execute_values(cur, """
                INSERT INTO talimat (
                    id, gonderen_id, alici_ekip_id, alici_user_id, baslik, icerik,
                    oncelik, okundu, okundu_tarihi, uygulanma_durumu, itiraz_metni, itiraz_tarihi, olusturma_tarihi
                ) VALUES %s
            """, [(
                t["id"], t["gonderen_id"], t["alici_ekip_id"], t["alici_user_id"], t["baslik"], t["icerik"],
                t["oncelik"], t["okundu"], t["okundu_tarihi"], t["uygulanma_durumu"], t["itiraz_metni"], t["itiraz_tarihi"], t["olusturma_tarihi"],
            ) for t in talimat_rows], page_size=200)

        if quest_rows:
            execute_values(cur, """
                INSERT INTO quest (
                    id, baslik, aciklama, hedef_deger, odul_xp, odul_rozet_id,
                    zorluk, kapsam, metrik, hedef_ekip_id, bitis_tarihi, olusturan_id, aktif, olusturma_tarihi
                ) VALUES %s
            """, [(
                q["id"], q["baslik"], q["aciklama"], q["hedef_deger"], q["odul_xp"], q["odul_rozet_id"],
                q["zorluk"], q["kapsam"], q["metrik"], q["hedef_ekip_id"], q["bitis_tarihi"], q["olusturan_id"], q["aktif"], q["olusturma_tarihi"],
            ) for q in quest_rows], page_size=200)

        if progress_rows:
            execute_values(cur, """
                INSERT INTO quest_ilerleme (id, quest_id, personel_id, mevcut_deger, durum, tamamlandi_at, olusturma_tarihi)
                VALUES %s
            """, [(
                p["id"], p["quest_id"], p["personel_id"], p["mevcut_deger"], p["durum"], p["tamamlandi_at"], p["olusturma_tarihi"],
            ) for p in progress_rows], page_size=200)

        rozetler = generate_rozetler()
        if rozetler:
            execute_values(cur, """
                INSERT INTO rozet (id, ad, aciklama, ikon_url, kategori, nadirlik, kosul_tipi, kosul_deger, kosul_aciklama, aktif, olusturma_tarihi)
                VALUES %s
            """, [(
                r["id"], r["ad"], r["aciklama"], r["ikon_url"], r["kategori"], r["nadirlik"], r["kosul_tipi"], r["kosul_deger"], r["kosul_aciklama"], r["aktif"], r["olusturma_tarihi"],
            ) for r in rozetler], page_size=200)

        rozet_assign = []
        for _ in range(random.randint(30, 40)):
            rozet_assign.append((
                random.choice(mh_ids), random.choice(rozetler)["id"], tz_dt(random.choice(list(daterange(BASLANGIC, BITIS))), time(12, 0))
            ))
        if rozet_assign:
            execute_values(cur, """
                INSERT INTO personel_rozet (personel_id, rozet_id, earned_at)
                VALUES %s ON CONFLICT DO NOTHING
            """, rozet_assign, page_size=200)

        kb_makaleler, kb_oneriler = generate_kb(content, admin_id, mh_ids)
        if kb_makaleler:
            execute_values(cur, """
                INSERT INTO kb_makale (id, baslik, icerik, kategori, alt_kategori, etiketler, yazar_id, aktif,
                    goruntuleme, faydali_oy, faydasiz_oy, olusturma_tarihi, guncelleme_tarihi)
                VALUES %s
            """, [(
                m["id"], m["baslik"], m["icerik"], m["kategori"], m["alt_kategori"], m["etiketler"], m["yazar_id"],
                m["aktif"], m["goruntuleme"], m["faydali_oy"], m["faydasiz_oy"], m["olusturma_tarihi"], m["guncelleme_tarihi"],
            ) for m in kb_makaleler], page_size=200)

        if kb_oneriler:
            execute_values(cur, """
                INSERT INTO kb_oneri (id, personel_id, baslik, icerik, onaylanan_icerik, kategori,
                    durum, supervisor_id, supervisor_notu, created_at)
                VALUES %s
            """, [(
                o["id"], o["personel_id"], o["baslik"], o["icerik"], o["onaylanan_icerik"], o["kategori"],
                o["durum"], o["supervisor_id"], o["supervisor_notu"], o["created_at"],
            ) for o in kb_oneriler], page_size=200)

        ajanda_rows = generate_ajanda(mh_ids, customers)
        if ajanda_rows:
            execute_values(cur, """
                INSERT INTO ajanda (id, user_id, musteri_id, tarih, saat, baslik, aciklama, tip, oncelik, durum, tekrar, olusturma_tarihi)
                VALUES %s
            """, [(
                a["id"], a["user_id"], a["musteri_id"], a["tarih"], a["saat"], a["baslik"], a["aciklama"],
                a["tip"], a["oncelik"], a["durum"], a["tekrar"], a["olusturma_tarihi"],
            ) for a in ajanda_rows], page_size=200)

        audit_rows = generate_audit(admin_id)
        if audit_rows:
            execute_values(cur, """
                INSERT INTO audit_log (id, user_id, eylem, hedef_tip, hedef_id, detay, ip_adresi, created_at)
                VALUES %s
            """, [(
                a["id"], a["user_id"], a["eylem"], a["hedef_tip"], a["hedef_id"], a["detay"], a["ip_adresi"], a["created_at"],
            ) for a in audit_rows], page_size=200)

        print("\n[13] Musteri istatistikleri...")
        cur.execute("""
            UPDATE musteri m SET
                toplam_cagri_sayisi = sub.cnt,
                son_arama_zamani = sub.son,
                ortalama_csat_skoru = sub.ort
            FROM (
                SELECT
                    cd.musteri_id,
                    COUNT(*)::int AS cnt,
                    MAX(cd.baslangic_zamani) AS son,
                    ROUND(AVG(cd.csat_skoru)::numeric, 2) AS ort
                FROM cagri_detay cd
                WHERE cd.musteri_id IS NOT NULL
                GROUP BY cd.musteri_id
            ) sub
            WHERE m.id = sub.musteri_id
        """)

        conn.commit()
        print("\nBAŞARILI — Senaryo verisi üretildi")

    except Exception as exc:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
