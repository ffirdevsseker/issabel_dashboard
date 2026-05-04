"""
Sporthink Çağrı Merkezi — Veritabanı Seed Generator
====================================================
Bu script seed_content.json dosyasını okuyup PostgreSQL'i
gerçekçi 12 aylık veriyle doldurur.

Çalıştırma:
    python generate_seed.py

Parametreler aşağıda CONFIG bölümünde değiştirilebilir.
"""

import json
import random
import uuid
import bcrypt
from datetime import datetime, timedelta, time
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

# ============================================================
# CONFIG — Burayı isterseniz değiştirebilirsiniz
# ============================================================

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "dashboard",
    "user":     "dashboard_user",
    "password": "Dashboard2026!",
}

# Veri parametreleri
MUSTERI_SAYISI          = 800       # 1 yıllık aktif müşteri sayısı
ZAMAN_ARALIGI_GUN       = 365       # Son kaç gün
GUNLUK_ORTALAMA_CAGRI   = 90        # Günlük tüm ekibin toplam çağrı sayısı
VARSAYILAN_SIFRE        = "Sporthink2026!"  # Tüm kullanıcılar için

# Rastgelelik için seed (aynı veri tekrar üretilebilir)
random.seed(42)

# Dosya yolu
JSON_PATH = Path(__file__).parent / "seed_content.json"

# ============================================================
# RESMİ TATİLLER (Türkiye, sabit + dini bayramlar)
# ============================================================

RESMI_TATILLER = set()

def _ekle_tatil(tarih_str):
    """YYYY-MM-DD formatında tarih ekle."""
    y, m, d = map(int, tarih_str.split("-"))
    RESMI_TATILLER.add(datetime(y, m, d).date())

# Sabit tatiller — son 2 yıl + bu yıl
for yil in [2024, 2025, 2026]:
    _ekle_tatil(f"{yil}-01-01")  # Yılbaşı
    _ekle_tatil(f"{yil}-04-23")  # Ulusal Egemenlik
    _ekle_tatil(f"{yil}-05-01")  # İşçi Bayramı
    _ekle_tatil(f"{yil}-05-19")  # Atatürk'ü Anma, Gençlik ve Spor
    _ekle_tatil(f"{yil}-07-15")  # Demokrasi ve Milli Birlik
    _ekle_tatil(f"{yil}-08-30")  # Zafer Bayramı
    _ekle_tatil(f"{yil}-10-29")  # Cumhuriyet Bayramı

# Ramazan Bayramı (yaklaşık)
_ekle_tatil("2025-03-30"); _ekle_tatil("2025-03-31"); _ekle_tatil("2025-04-01")
_ekle_tatil("2026-03-20"); _ekle_tatil("2026-03-21"); _ekle_tatil("2026-03-22")

# Kurban Bayramı (yaklaşık)
_ekle_tatil("2025-06-06"); _ekle_tatil("2025-06-07"); _ekle_tatil("2025-06-08"); _ekle_tatil("2025-06-09")
_ekle_tatil("2026-05-26"); _ekle_tatil("2026-05-27"); _ekle_tatil("2026-05-28"); _ekle_tatil("2026-05-29")

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def hash_sifre(sifre: str) -> str:
    """Şifreyi bcrypt ile hashler."""
    return bcrypt.hashpw(sifre.encode(), bcrypt.gensalt()).decode()

def rastgele_telefon() -> str:
    """05XX XXX XX XX formatında rastgele telefon numarası."""
    operator = random.choice(["530","531","532","533","534","535","536","537","538","539",
                              "540","541","542","543","544","545","546","547","548","549",
                              "550","551","552","553","554","555","556","557","558","559"])
    return f"0{operator}{random.randint(1000000, 9999999)}"

def rastgele_email(ad: str, soyad: str) -> str:
    """Türkçe karakterleri kaldırıp e-posta üretir."""
    cevirim = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    ad_temiz = ad.translate(cevirim).lower().replace(" ", "")
    soyad_temiz = soyad.translate(cevirim).lower().replace(" ", "")
    domain = random.choice(["gmail.com", "hotmail.com", "outlook.com", "yandex.com"])
    return f"{ad_temiz}.{soyad_temiz}{random.randint(1,99)}@{domain}"

def rastgele_zaman_dagilimi() -> int:
    """
    Saatlik çağrı dağılımı (gerçekçi).
    Sabah ve öğleden sonra yoğun, öğle arası az.
    """
    saatler  = [9, 10, 11, 12, 13, 14, 15, 16, 17]
    agirlik  = [15, 18, 17, 8,  5,  12, 14, 11, 6]
    return random.choices(saatler, weights=agirlik)[0]

def is_calisma_gunu(tarih: datetime) -> bool:
    """Hafta içi mi VE resmi tatil değil mi?"""
    if tarih.weekday() >= 5:  # Cumartesi=5, Pazar=6
        return False
    # date olarak kontrol et
    t = tarih.date() if hasattr(tarih, 'date') else tarih
    return t not in RESMI_TATILLER

def kategori_sec(kategoriler: dict) -> str:
    """Ağırlıklı kategori seçimi."""
    isimler = list(kategoriler.keys())
    agirlik = [k["agirlik"] for k in kategoriler.values()]
    return random.choices(isimler, weights=agirlik)[0]

def sure_uret(ortalama_dk: float, performans: str) -> int:
    """Performansa göre çağrı süresi (saniye)."""
    carpan = {"yuksek": 0.85, "orta": 1.0, "dusuk": 1.25, "yeni": 1.4}[performans]
    sure_dk = max(0.5, random.gauss(ortalama_dk * carpan, ortalama_dk * 0.3))
    return int(sure_dk * 60)

def csat_uret(ortalama: float) -> int:
    """Ortalama etrafında CSAT skoru üret."""
    skor = random.gauss(ortalama, 0.7)
    return max(1, min(5, round(skor)))

def progress(mesaj: str):
    print(f"  → {mesaj}")

# ============================================================
# 1. ROLLER (Mevcut, sadece ID'leri al)
# ============================================================

def roller_yukle(cur):
    progress("Roller yükleniyor...")
    cur.execute("SELECT id, name FROM roles")
    return {row[1]: row[0] for row in cur.fetchall()}

# ============================================================
# 2. DEPARTMAN ve EKİP (Mevcut, sadece ID'leri al)
# ============================================================

def departman_ekip_yukle(cur):
    progress("Departmanlar yükleniyor...")
    cur.execute("SELECT id, ad FROM departman")
    departmanlar = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT id, ad FROM ekip")
    ekipler = {row[1]: row[0] for row in cur.fetchall()}

    return departmanlar, ekipler

# ============================================================
# 3. KULLANICILAR
# ============================================================

def kullanicilar_olustur(cur, content, roller, ekipler):
    progress("Kullanıcılar oluşturuluyor...")
    user_ids = {}
    sifre_hash = hash_sifre(VARSAYILAN_SIFRE)

    for p in content["personeller"]:
        uid = str(uuid.uuid4())
        # Vardiya saatleri JSON'dan
        v_bas_str = p.get("vardiya_baslangic", "09:00")
        v_bit_str = p.get("vardiya_bitis", "18:00")
        v_bas = time(int(v_bas_str.split(":")[0]), int(v_bas_str.split(":")[1]))
        v_bit = time(int(v_bit_str.split(":")[0]), int(v_bit_str.split(":")[1]))

        # İşe başlama tarihi
        ise_baslama_gun_once = p.get("ise_baslama_gun_once", 365)
        ise_baslama = (datetime.now() - timedelta(days=ise_baslama_gun_once)).date()

        # Performansa göre izin/rapor günü sayısı
        perf = p["performans"]
        if perf == "yuksek":
            yillik_izin = random.randint(14, 18)
            rapor_gun = random.randint(1, 3)
        elif perf == "orta":
            yillik_izin = random.randint(15, 20)
            rapor_gun = random.randint(2, 5)
        elif perf == "dusuk":
            yillik_izin = random.randint(15, 20)
            rapor_gun = random.randint(5, 10)  # düşük perf = daha fazla rapor
        else:  # yeni
            yillik_izin = random.randint(3, 7)  # yeni başladığı için az izin
            rapor_gun = random.randint(0, 2)

        # Geçen süreye orantılı izin (1 yıldan az çalışan için pro-rata)
        oran = min(1.0, ise_baslama_gun_once / 365.0)
        izin_gun_sayisi = max(1, int(yillik_izin * oran))
        rapor_gun_sayisi = max(0, int(rapor_gun * oran))

        # Rastgele izin günleri seç (iş başlama tarihinden bugüne)
        izin_gunleri = set()
        rapor_gunleri = set()
        bugun_d = datetime.now().date()
        gecerli_gunler = []
        d = ise_baslama
        while d <= bugun_d:
            if d.weekday() < 5 and d not in RESMI_TATILLER:
                gecerli_gunler.append(d)
            d += timedelta(days=1)

        if len(gecerli_gunler) >= izin_gun_sayisi + rapor_gun_sayisi:
            secilen = random.sample(gecerli_gunler, izin_gun_sayisi + rapor_gun_sayisi)
            izin_gunleri = set(secilen[:izin_gun_sayisi])
            rapor_gunleri = set(secilen[izin_gun_sayisi:])

        user_ids[p["username"]] = {
            "id": uid,
            "performans": p["performans"],
            "rol": p["rol"],
            "ekip": p.get("ekip"),
            "extension": p["extension"],
            "vardiya_baslangic": v_bas,
            "vardiya_bitis": v_bit,
            "ise_baslama": ise_baslama,
            "izin_gunleri": izin_gunleri,
            "rapor_gunleri": rapor_gunleri,
        }

        cur.execute("""
            INSERT INTO users (
                id, username, email, phone, display_name, hashed_password,
                role_id, extension, is_active, current_status,
                xp, level, tier, vardiya_baslangic, vardiya_bitis,
                last_login
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            uid,
            p["username"],
            rastgele_email(p["ad"], p["soyad"]),
            rastgele_telefon(),
            f"{p['ad']} {p['soyad']}",
            sifre_hash,
            roller[p["rol"]],
            p["extension"],
            True,
            random.choice(["aktif", "mola", "mesgul", "offline"]) if p["rol"] == "personel" else "offline",
            0,  # XP sonra hesaplanacak
            1,
            "bronz",
            v_bas,
            v_bit,
            datetime.now() - timedelta(hours=random.randint(1, 48)),
        ))

        # Ekip ataması (sadece personel)
        if p.get("ekip") and p["ekip"] in ekipler:
            cur.execute("""
                INSERT INTO personel_ekip (personel_id, ekip_id)
                VALUES (%s, %s)
            """, (uid, ekipler[p["ekip"]]))

    # Supervisor ekipleri
    supervisor_ids = [v["id"] for v in user_ids.values() if v["rol"] == "supervisor"]
    if supervisor_ids:
        ekip_listesi = list(ekipler.values())
        for i, sup_id in enumerate(supervisor_ids):
            for ekip_id in ekip_listesi[i::len(supervisor_ids)]:
                cur.execute("""
                    INSERT INTO supervisor_ekip (supervisor_id, ekip_id)
                    VALUES (%s, %s)
                """, (sup_id, ekip_id))

    # Kullanıcı tercihleri (her kullanıcı için)
    for username, info in user_ids.items():
        cur.execute("""
            INSERT INTO kullanici_tercih (user_id) VALUES (%s)
        """, (info["id"],))

    progress(f"    {len(user_ids)} kullanıcı oluşturuldu")
    return user_ids

# ============================================================
# 4. MÜŞTERİLER
# ============================================================

def musteriler_olustur(cur, content, user_ids):
    progress(f"{MUSTERI_SAYISI} müşteri oluşturuluyor...")
    musteri_listesi = []
    isimler = content["musteri_isimleri"]
    olusturan_id = next(iter(user_ids.values()))["id"]  # admin

    for i in range(MUSTERI_SAYISI):
        isim = random.choice(isimler)
        # Müşteri davranış profili
        r = random.random()
        if r < 0.10:
            kategori = "vip"
        elif r < 0.40:
            kategori = "standart"
        else:
            kategori = "yeni"

        # Müşterinin ilk iletişimi - geniş aralıkta, çoğu eski müşteri
        # (Çağrı sürekli olabilsin diye 2 yıla kadar geri git)
        ilk_iletisim_offset = random.randint(30, 730)
        ilk_iletisim = datetime.now() - timedelta(days=ilk_iletisim_offset)
        mid = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO musteri (
                id, ad, soyad, telefon, email, kategori,
                kaynak, ilk_iletisim, son_iletisim,
                toplam_gorusme, olusturan_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            mid,
            isim["ad"],
            isim["soyad"],
            rastgele_telefon(),
            rastgele_email(isim["ad"], isim["soyad"]) if random.random() > 0.3 else None,
            kategori,
            "manuel",
            ilk_iletisim,
            ilk_iletisim,
            0,
            olusturan_id,
        ))

        # Çağrı dağılımı için her müşterinin "tip"ini belirle
        r = random.random()
        if r < 0.25:
            tip = "tek_seferlik"
            cagri_sayisi = random.randint(1, 2)
        elif r < 0.65:
            tip = "ara_sira"
            cagri_sayisi = random.randint(3, 5)
        elif r < 0.90:
            tip = "sik"
            cagri_sayisi = random.randint(6, 10)
        else:
            tip = "vip_kronik"
            cagri_sayisi = random.randint(11, 25)

        musteri_listesi.append({
            "id": mid,
            "kategori": kategori,
            "tip": tip,
            "cagri_sayisi": cagri_sayisi,
            "ilk_iletisim": ilk_iletisim,
        })

    progress(f"    {len(musteri_listesi)} müşteri oluşturuldu")
    return musteri_listesi

# ============================================================
# 5. ÇAĞRILAR (Ana iş — en uzun bölüm)
# ============================================================

def cagrilar_olustur(cur, content, user_ids, musteriler):
    progress("Çağrılar oluşturuluyor (bu bölüm uzun sürebilir)...")

    # Sadece personel role'ündekiler çağrı cevaplar
    personel_listesi = {u: i for u, i in user_ids.items() if i["rol"] == "personel"}
    perf_profili = content["performans_profilleri"]
    kategoriler = content["cagri_kategorileri"]
    notlar_havuz = content["cagri_notlari"]
    ai_sablonlar = content["ai_ozet_sablonlari"]
    urunler = content["sporthink_urunleri"]

    cagri_kayitlari = []
    not_kayitlari = []
    csat_kayitlari = []
    ai_ozet_kayitlari = []
    musteri_son_iletisim = {}  # müşteri_id -> son tarih

    # Her personelin çalıştığı (vardiya olduğu) günler hesapla
    progress("Personel çalışma günleri hesaplanıyor...")
    personel_calisma_gunleri = {}
    bugun_d = datetime.now().date()
    for username, info in personel_listesi.items():
        gunler = []
        d = info["ise_baslama"]
        while d <= bugun_d:
            if (d.weekday() < 5 and
                d not in RESMI_TATILLER and
                d not in info["izin_gunleri"] and
                d not in info["rapor_gunleri"]):
                gunler.append(d)
            d += timedelta(days=1)
        personel_calisma_gunleri[username] = gunler
        progress(f"    {username}: {len(gunler)} gün çalışmış")

    # Mevsimsel ağırlıklar (Sporthink)
    aylik_carpan = {
        1:  0.7,   2:  0.85,  3:  1.2,   4:  1.0,
        5:  0.9,   6:  1.3,   7:  0.75,  8:  0.7,
        9:  1.4,   10: 1.1,   11: 1.6,   12: 1.5,
    }

    # Performansa göre günlük çağrı kapasitesi
    perf_gunluk_cagri = {
        "yuksek": (14, 18),
        "orta":   (10, 13),
        "dusuk":  (7, 10),
        "yeni":   (5, 8),
    }

    cagri_index = 0

    # YENİ MANTIK: Her personel için, çalıştığı her güne çağrı ata
    for username, info in personel_listesi.items():
        performans = info["performans"]
        profil = perf_profili[performans]
        gunluk_min, gunluk_max = perf_gunluk_cagri[performans]
        calisma_gunleri = personel_calisma_gunleri[username]

        for tarih in calisma_gunleri:
            # Bu güne mevsimsel çarpan uygula
            carpan = aylik_carpan[tarih.month]
            gunluk_cagri = int(random.randint(gunluk_min, gunluk_max) * carpan)

            for _ in range(gunluk_cagri):
                cagri_index += 1

                # Saat dağılımı (vardiya saatlerine göre)
                vbas = info["vardiya_baslangic"].hour
                vbit = info["vardiya_bitis"].hour
                if vbit - vbas < 9:
                    vbit = vbas + 9
                # Ağırlıklı saat seçimi (sabah ve öğleden sonra yoğun)
                saat_havuzu = list(range(vbas, vbit))
                if len(saat_havuzu) >= 9:
                    agirlik = [15, 18, 17, 8, 5, 12, 14, 11, 6][:len(saat_havuzu)]
                else:
                    agirlik = [10] * len(saat_havuzu)
                saat = random.choices(saat_havuzu, weights=agirlik)[0]
                dakika = random.randint(0, 59)
                cagri_zamani = datetime.combine(tarih, time(saat, dakika, random.randint(0, 59)))

                # Müşteri seç (mevcut müşterilerden ağırlıklı)
                # Sık arayan müşteriler daha sık seçilsin
                musteri = random.choice(musteriler)
                # Müşterinin ilk iletişiminden önceyse atla
                if cagri_zamani < musteri["ilk_iletisim"]:
                    musteri = random.choice([m for m in musteriler if m["ilk_iletisim"] <= cagri_zamani])

                # Cevapsız mı?
                cevapsiz = random.random() < profil["cevapsiz_orani"]

                # Kategori
                kategori = kategori_sec(kategoriler)
                kat_data = kategoriler[kategori]

                # Aktarım?
                aktarim_olasilik = {
                    "siparis_takibi": 0.05, "iade_degisim": 0.10,
                    "urun_bilgisi": 0.08,   "kargo_sorunu": 0.15,
                    "odeme_fatura": 0.30,   "sikayet": 0.20, "diger": 0.25,
                }.get(kategori, 0.05)

                aktarildi = (not cevapsiz) and (random.random() < aktarim_olasilik)
                aktarilan_dep = None
                if aktarildi:
                    aktarilan_dep = random.choice([
                        "muhasebe", "e_ticaret", "depo_stok", "it"
                    ])

                # Çağrı sonucu
                if cevapsiz:
                    cagri_sonucu = "cevaplanmadi"
                elif aktarildi:
                    cagri_sonucu = "aktarildi"
                else:
                    cagri_sonucu = "cevaplandi"

                # Süre
                if cevapsiz:
                    sure = random.randint(15, 30)
                else:
                    sure = sure_uret(kat_data["ortalama_sure_dk"], performans)
                bitis = cagri_zamani + timedelta(seconds=sure)

                # Bekleme süresi
                bekleme = random.randint(5, 60) if random.random() > 0.3 else random.randint(0, 5)

                cagri_id = str(uuid.uuid4())

                cagri_kayitlari.append((
                    cagri_id,
                    f"sporthink-{cagri_index:08d}",  # cdr_uniqueid (sahte)
                    info["id"],  # cevapsız da olsa personele atandı (kuyruğa düştü)
                    musteri["id"],
                    rastgele_telefon(),
                    "0232 442 07 07",
                    "gelen",
                    "queue_mh",
                    kat_data["ivr_yolu"],
                    info["extension"],
                    cagri_zamani,
                    bitis,
                    sure,
                    bekleme,
                    kategori,
                    None,
                    False,
                    None,
                    None,
                    None,
                    aktarildi,
                    aktarilan_dep,
                    info["id"] if aktarildi else None,
                    f"Müşteri talebi {aktarilan_dep} departmanını gerektiriyordu" if aktarildi else None,
                    cagri_sonucu,
                ))

                musteri_son_iletisim[musteri["id"]] = cagri_zamani

                # Cevapsız ise burada bitir
                if cevapsiz:
                    continue

                # Not yazılma olasılığı
                if random.random() < profil["not_yazma_orani"] and notlar_havuz.get(kategori):
                    not_metni = random.choice(notlar_havuz[kategori])
                    not_metni = not_metni.replace("{URUN}", random.choice(urunler))
                    not_metni = not_metni.replace("{SIPARIS}", str(random.randint(100000, 999999)))
                    not_metni = not_metni.replace("{SEHIR}", random.choice(content["sehirler"]))
                    not_metni = not_metni.replace("{MARKA}", random.choice(["Nike","Adidas","Puma","Vans","Converse"]))

                not_kayitlari.append((
                    str(uuid.uuid4()),
                    cagri_id,
                    musteri["id"],
                    info["id"],
                    not_metni,
                    kategori,
                    [random.choice(["iade","kargo","ürün","ödeme","beden"])],
                    random.choice(["dusuk","orta","yuksek"]),
                    cagri_zamani,
                ))

            # CSAT (rastgele 40% oran)
            if random.random() < 0.40:
                csat_skoru = csat_uret(profil["csat_ortalama"])
                csat_kayitlari.append((
                    str(uuid.uuid4()),
                    cagri_id,
                    musteri["id"],
                    info["id"],
                    csat_skoru,
                    None,
                    cagri_zamani + timedelta(minutes=random.randint(5, 30)),
                ))

            # AI özet (50% oran)
            if random.random() < 0.50 and ai_sablonlar.get(kategori):
                ozet = random.choice(ai_sablonlar[kategori])
                ozet = ozet.replace("{URUN}", random.choice(urunler))

                ai_id = str(uuid.uuid4())
                ai_ozet_kayitlari.append((
                    ai_id,
                    cagri_id,
                    ozet,
                    None,
                    None,
                    [random.choice(["sipariş","iade","stok","kargo","beden"])],
                    random.choice(["pozitif","notr","negatif"]),
                    random.choice(["dusuk","orta","yuksek"]),
                    "claude-sonnet-4",
                    cagri_zamani + timedelta(seconds=sure + 10),
                ))

    # Toplu insert (hızlı)
    progress(f"    {len(cagri_kayitlari)} çağrı kaydı yazılıyor...")
    execute_values(cur, """
        INSERT INTO cagri_detay (
            id, cdr_uniqueid, personel_id, musteri_id,
            arayan_no, aranan_no, cagri_yonu, kuyruk_adi,
            ivr_yolu, dahili_no, baslangic_zamani, bitis_zamani,
            sure_saniye, bekleme_suresi_saniye, kategori,
            ai_ozet_id, ai_ozet_onaylandi, ses_kaydi_url, ses_kaydi_sure,
            csat_skoru,
            aktarim_yapildi_mi, aktarilan_departman, aktaran_personel_id,
            aktarim_nedeni, cagri_sonucu
        ) VALUES %s
    """, cagri_kayitlari, page_size=500)

    progress(f"    {len(not_kayitlari)} not yazılıyor...")
    if not_kayitlari:
        execute_values(cur, """
            INSERT INTO cagri_notu (
                id, cagri_id, musteri_id, personel_id,
                icerik, kategori, etiketler, oncelik, olusturma_tarihi
            ) VALUES %s
        """, not_kayitlari, page_size=500)

    progress(f"    {len(csat_kayitlari)} CSAT kaydı yazılıyor...")
    if csat_kayitlari:
        execute_values(cur, """
            INSERT INTO csat (
                id, cagri_id, musteri_id, personel_id,
                skor, yorum, olusturma_tarihi
            ) VALUES %s
        """, csat_kayitlari, page_size=500)

    progress(f"    {len(ai_ozet_kayitlari)} AI özet yazılıyor...")
    if ai_ozet_kayitlari:
        execute_values(cur, """
            INSERT INTO ai_ozet (
                id, cagri_id, ozet_metni, musteri_talebi,
                sonraki_adim, anahtar_kelimeler, duygu_skoru,
                duygu_yogunlugu, model, olusturma_tarihi
            ) VALUES %s
        """, ai_ozet_kayitlari, page_size=500)

    return cagri_kayitlari, csat_kayitlari

# ============================================================
# 6. MÜŞTERİ İSTATİSTİKLERİNİ GÜNCELLE
# ============================================================

def musteri_istatistik_guncelle(cur):
    progress("Müşteri istatistikleri güncelleniyor...")
    cur.execute("""
        UPDATE musteri m SET
            toplam_gorusme = sub.cnt,
            son_iletisim   = sub.son,
            ortalama_csat  = sub.csat
        FROM (
            SELECT
                cd.musteri_id,
                COUNT(*) AS cnt,
                MAX(cd.baslangic_zamani) AS son,
                AVG(c.skor)::DECIMAL(3,2) AS csat
            FROM cagri_detay cd
            LEFT JOIN csat c ON c.cagri_id = cd.id
            WHERE cd.musteri_id IS NOT NULL
            GROUP BY cd.musteri_id
        ) sub
        WHERE m.id = sub.musteri_id
    """)

# ============================================================
# 7. XP HAREKETLERİ ve KULLANICI XP/LEVEL
# ============================================================

def xp_uret(cur, content, user_ids):
    progress("XP hareketleri üretiliyor...")
    perf_profili = content["performans_profilleri"]

    # Çağrı bazlı XP üret
    cur.execute("""
        SELECT id, personel_id, sure_saniye, kategori, csat_skoru,
               cagri_sonucu, baslangic_zamani
        FROM cagri_detay
        WHERE personel_id IS NOT NULL
        ORDER BY baslangic_zamani
    """)

    xp_kayitlari = []
    personel_xp_top = {}

    for row in cur.fetchall():
        cagri_id, p_id, sure, kategori, csat, sonuc, tarih = row

        if sonuc == "cevaplanmadi":
            xp_kayitlari.append((
                str(uuid.uuid4()), p_id, -5, "Cevapsız çağrı",
                cagri_id, "cagri", tarih
            ))
            personel_xp_top[p_id] = personel_xp_top.get(p_id, 0) - 5
            continue

        # Çağrı tamamlama
        xp = 10
        xp_kayitlari.append((
            str(uuid.uuid4()), p_id, 10, "Çağrı tamamlama",
            cagri_id, "cagri", tarih
        ))

        # Kısa süre bonusu
        if sure and sure < 180:
            xp_kayitlari.append((
                str(uuid.uuid4()), p_id, 5, "Hızlı çözüm bonusu",
                cagri_id, "cagri", tarih
            ))
            xp += 5

        # CSAT bonusu
        if csat and csat >= 4:
            xp_kayitlari.append((
                str(uuid.uuid4()), p_id, 15, f"Yüksek CSAT ({csat} yıldız)",
                cagri_id, "cagri", tarih
            ))
            xp += 15
        elif csat and csat <= 2:
            xp_kayitlari.append((
                str(uuid.uuid4()), p_id, -10, f"Düşük CSAT ({csat} yıldız)",
                cagri_id, "cagri", tarih
            ))
            xp -= 10

        personel_xp_top[p_id] = personel_xp_top.get(p_id, 0) + xp

    # Toplu yaz
    progress(f"    {len(xp_kayitlari)} XP hareketi yazılıyor...")
    execute_values(cur, """
        INSERT INTO xp_hareketi (
            id, personel_id, miktar, sebep, referans_id, referans_tip, olusturma_tarihi
        ) VALUES %s
    """, xp_kayitlari, page_size=1000)

    # Kullanıcıların XP ve level'ini güncelle
    progress("Kullanıcı XP ve seviyeleri hesaplanıyor...")
    for p_id, top_xp in personel_xp_top.items():
        # Seviye hesapla (basit formül)
        if top_xp < 1000:
            level = 1 + (top_xp // 100)
            tier = "bronz"
        elif top_xp < 3000:
            level = 11 + ((top_xp - 1000) // 200)
            tier = "gumus"
        elif top_xp < 7000:
            level = 21 + ((top_xp - 3000) // 400)
            tier = "altin"
        else:
            level = 31 + ((top_xp - 7000) // 500)
            tier = "platin"

        cur.execute("""
            UPDATE users SET xp = %s, level = %s, tier = %s
            WHERE id = %s
        """, (top_xp, min(level, 40), tier, p_id))

# ============================================================
# 8. ROZETLER
# ============================================================

def rozetler_olustur(cur, content, user_ids):
    progress("Rozetler oluşturuluyor...")
    rozet_ids = {}

    for r in content["rozetler"]:
        rid = str(uuid.uuid4())
        rozet_ids[r["ad"]] = rid
        cur.execute("""
            INSERT INTO rozet (id, ad, aciklama, kategori, nadirlik, kosul_aciklama)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rid, r["ad"], r["kosul"], r["kategori"], r["nadirlik"], r["kosul"]))

    # Personellere rozet dağıt
    cur.execute("""
        SELECT u.id, u.xp,
               (SELECT COUNT(*) FROM cagri_detay WHERE personel_id = u.id) AS cagri
        FROM users u
        WHERE role_id = (SELECT id FROM roles WHERE name = 'personel')
    """)

    rozet_atamalari = []
    for u_id, xp, cagri_sayisi in cur.fetchall():
        # İlk Çağrı (herkes alır)
        if cagri_sayisi >= 1:
            rozet_atamalari.append((u_id, rozet_ids["İlk Çağrı"], datetime.now() - timedelta(days=300)))
        if cagri_sayisi >= 100:
            rozet_atamalari.append((u_id, rozet_ids["100. Çağrı"], datetime.now() - timedelta(days=200)))
        if cagri_sayisi >= 1000:
            rozet_atamalari.append((u_id, rozet_ids["1000. Çağrı"], datetime.now() - timedelta(days=50)))
        if xp > 2000:
            rozet_atamalari.append((u_id, rozet_ids["İlk Hafta"], datetime.now() - timedelta(days=350)))
            rozet_atamalari.append((u_id, rozet_ids["İlk Ay"], datetime.now() - timedelta(days=320)))
        if xp > 5000:
            rozet_atamalari.append((u_id, rozet_ids["Sürekli Asker"], datetime.now() - timedelta(days=200)))

    if rozet_atamalari:
        execute_values(cur, """
            INSERT INTO personel_rozet (personel_id, rozet_id, earned_at)
            VALUES %s ON CONFLICT DO NOTHING
        """, rozet_atamalari)

    progress(f"    {len(content['rozetler'])} rozet, {len(rozet_atamalari)} atama")

# ============================================================
# 9. QUESTLER
# ============================================================

def questler_olustur(cur, content, user_ids):
    progress("Questler oluşturuluyor...")
    admin_id = next((v["id"] for v in user_ids.values() if v["rol"] == "admin"), None)

    quest_ids = []
    for q in content["questler"]:
        qid = str(uuid.uuid4())
        quest_ids.append(qid)
        cur.execute("""
            INSERT INTO quest (
                id, baslik, aciklama, hedef_deger, odul_xp,
                zorluk, kapsam, metrik, bitis_tarihi, olusturan_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            qid, q["baslik"], q["baslik"], q["hedef"], q["odul_xp"],
            q["zorluk"], q["kapsam"], q.get("metrik"),
            datetime.now().date() + timedelta(days=1), admin_id
        ))

    # Her personele quest ilerlemesi ata
    personel_ids = [v["id"] for v in user_ids.values() if v["rol"] == "personel"]
    ilerlemeler = []
    for p_id in personel_ids:
        for q_id in quest_ids:
            mevcut = random.randint(0, 15)
            durum = "tamamlandi" if mevcut >= 10 else "aktif"
            ilerlemeler.append((
                str(uuid.uuid4()), q_id, p_id, mevcut, durum,
                datetime.now() - timedelta(hours=random.randint(1, 12)) if durum == "tamamlandi" else None,
                datetime.now() - timedelta(hours=random.randint(1, 24))
            ))

    if ilerlemeler:
        execute_values(cur, """
            INSERT INTO quest_ilerleme (
                id, quest_id, personel_id, mevcut_deger, durum,
                tamamlandi_at, olusturma_tarihi
            ) VALUES %s ON CONFLICT (quest_id, personel_id) DO NOTHING
        """, ilerlemeler)

    progress(f"    {len(quest_ids)} quest, {len(ilerlemeler)} ilerleme kaydı")

# ============================================================
# 10. KB MAKALELERİ
# ============================================================

def kb_olustur(cur, content, user_ids):
    progress("KB makaleleri oluşturuluyor...")
    admin_id = next((v["id"] for v in user_ids.values() if v["rol"] == "admin"), None)

    for m in content["kb_makaleleri"]:
        cur.execute("""
            INSERT INTO kb_makale (
                id, baslik, icerik, kategori, alt_kategori,
                etiketler, yazar_id, goruntuleme
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            m["baslik"],
            m["icerik"],
            m["kategori"],
            m["alt_kategori"],
            m["etiketler"],
            admin_id,
            random.randint(5, 200),
        ))

    progress(f"    {len(content['kb_makaleleri'])} makale eklendi")

# ============================================================
# 11. VARDİYALAR ve MOLALAR
# ============================================================

def vardiya_mola_olustur(cur, user_ids):
    progress("Vardiya ve molalar oluşturuluyor (sadece çalışılan günler)...")
    # Sadece personel role'ündekiler
    personel_data = [(v["id"], v["vardiya_baslangic"], v["vardiya_bitis"],
                      v["ise_baslama"], v["izin_gunleri"], v["rapor_gunleri"])
                     for v in user_ids.values() if v["rol"] == "personel"]

    bugun = datetime.now().date()
    vardiya_kayit = []
    mola_kayit = []

    for p_id, v_bas, v_bit, ise_bas, izin_g, rapor_g in personel_data:
        # Mola saat aralığı
        mola_saat_min = v_bas.hour + 2
        mola_saat_max = min(v_bit.hour - 2, mola_saat_min + 6)

        d = ise_bas
        while d <= bugun:
            # Hafta içi VE resmi tatil değil VE izinde değil VE raporlu değil
            if (d.weekday() < 5 and
                d not in RESMI_TATILLER and
                d not in izin_g and
                d not in rapor_g):

                vardiya_kayit.append((
                    str(uuid.uuid4()), p_id, d, "normal",
                    v_bas, v_bit, None
                ))

                # Bu güne 1-2 mola ekle
                for _ in range(random.randint(1, 2)):
                    bas_saat = random.randint(mola_saat_min, mola_saat_max)
                    bas = datetime.combine(d, time(bas_saat, random.randint(0,59)))
                    sure = random.randint(10, 30)
                    bit = bas + timedelta(minutes=sure)
                    planlanan = bas + timedelta(minutes=15)
                    durum = "uzun" if sure > 20 else "tamamlandi"
                    mola_kayit.append((
                        str(uuid.uuid4()), p_id, bas, bit, planlanan,
                        "standart", durum, None, None, bas
                    ))
            d += timedelta(days=1)

    if vardiya_kayit:
        execute_values(cur, """
            INSERT INTO vardiya (id, personel_id, tarih, tip, baslangic, bitis, olusturan_id)
            VALUES %s
        """, vardiya_kayit, page_size=1000)

    if mola_kayit:
        execute_values(cur, """
            INSERT INTO mola (
                id, personel_id, baslangic, bitis, planlanan_bitis,
                tur, durum, supervisor_id, supervisor_notu, created_at
            ) VALUES %s
        """, mola_kayit, page_size=1000)

    progress(f"    {len(vardiya_kayit)} vardiya, {len(mola_kayit)} mola")

# ============================================================
# ANA AKIŞ
# ============================================================

def main():
    print("=" * 60)
    print("Sporthink Çağrı Merkezi — Seed Generator")
    print("=" * 60)

    # JSON yükle
    print(f"\n[1/11] JSON içerik yükleniyor: {JSON_PATH}")
    if not JSON_PATH.exists():
        print(f"HATA: {JSON_PATH} bulunamadı!")
        return
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        content = json.load(f)
    progress(f"İçerik yüklendi: {len(content['personeller'])} personel, "
             f"{len(content['musteri_isimleri'])} müşteri ismi havuzu")

    # DB bağlan
    print(f"\n[2/11] PostgreSQL bağlantısı: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()
        progress("Bağlantı kuruldu")
    except Exception as e:
        print(f"BAĞLANTI HATASI: {e}")
        return

    try:
        # Mevcut verileri temizle (sadece seed verisi)
        print("\n[3/11] Eski seed verileri temizleniyor...")
        for tbl in ["xp_hareketi", "personel_rozet", "quest_ilerleme", "quest", "rozet",
                    "ai_ozet", "csat", "cagri_notu", "cagri_detay",
                    "mesaj", "bildirim", "talimat", "sikayet", "kb_oneri", "kb_makale",
                    "ticket", "ajanda", "mola", "mola_kurali", "vardiya_talep", "vardiya",
                    "musteri", "kullanici_tercih", "supervisor_ekip", "personel_ekip",
                    "audit_log"]:
            cur.execute(f"DELETE FROM {tbl}")
        # users'tan sadece seed kullanıcıları sil (rolleri ve departmanları koru)
        cur.execute("DELETE FROM users")
        progress("Tablolar temizlendi")

        # Adımlar
        print("\n[4/11] Roller, departman, ekipler...")
        roller = roller_yukle(cur)
        departmanlar, ekipler = departman_ekip_yukle(cur)

        print("\n[5/11] Kullanıcılar...")
        user_ids = kullanicilar_olustur(cur, content, roller, ekipler)

        print("\n[6/11] Müşteriler...")
        musteriler = musteriler_olustur(cur, content, user_ids)

        print("\n[7/11] Çağrılar (en uzun adım)...")
        cagri_kayitlari, csat_kayitlari = cagrilar_olustur(cur, content, user_ids, musteriler)

        print("\n[8/11] Müşteri istatistikleri...")
        musteri_istatistik_guncelle(cur)

        print("\n[9/11] XP & seviyeler...")
        xp_uret(cur, content, user_ids)

        print("\n[10/11] Rozetler & Questler...")
        rozetler_olustur(cur, content, user_ids)
        questler_olustur(cur, content, user_ids)

        print("\n[11/11] KB, Vardiya, Mola...")
        kb_olustur(cur, content, user_ids)
        vardiya_mola_olustur(cur, user_ids)

        # COMMIT
        conn.commit()

        # Özet
        print("\n" + "=" * 60)
        print("BAŞARILI — Veritabanı dolduruldu")
        print("=" * 60)
        cur.execute("SELECT COUNT(*) FROM users")
        print(f"  Kullanıcı:    {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM musteri")
        print(f"  Müşteri:      {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM cagri_detay")
        print(f"  Çağrı:        {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM cagri_notu")
        print(f"  Not:          {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM csat")
        print(f"  CSAT:         {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM xp_hareketi")
        print(f"  XP hareketi:  {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM personel_rozet")
        print(f"  Rozet (atama):{cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM kb_makale")
        print(f"  KB makale:    {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM vardiya")
        print(f"  Vardiya:      {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM mola")
        print(f"  Mola:         {cur.fetchone()[0]}")
        print("\nGiriş bilgileri:")
        print(f"  Kullanıcı adı: admin / supervisor1 / ahmet.kaya  (vs)")
        print(f"  Şifre:         {VARSAYILAN_SIFRE}")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        import traceback
        print(f"\nHATA — Tüm değişiklikler geri alındı:")
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()