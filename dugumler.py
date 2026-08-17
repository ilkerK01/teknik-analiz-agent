from durum import Durum
from kurallar import BAYRAK_METINLERI, BELIRTI_KODLARI, triyaj_yap
from model import model_getir
from promptlar import ANALIZ_PROMPT,COZUM_PROMPT,SERVIS_BASLIK,SERVIS_SABLONU_ADIMLARI,TON_METINLERI
from semalar import AnalizSonucu, CozumSonucu


# LANGGRAPH'IN EN COK SASIRTAN KURALI:
# Node fonksiyonu tum Durum'u dondurmez. Sadece DEGISTIRDIGI alanlari
# bir sozluk olarak dondurur. LangGraph onu mevcut state'in ustune
# birlestirir. Bunu ilk seferde herkes yanlis yapar.
#
# Ayrica node'lar durum["alan"] yerine durum.get("alan", varsayilan)
# kullaniyor. Sebep: grafigi sadece {"sikayet": "..."} ile baslatiyoruz,
# diger alanlar henuz yok. Kose parantezle erisirsen KeyError alirsin.


def analiz(durum: Durum) -> dict:
    """Ham sikayeti yapilandirilmis veriye cevirir. LLM kullanir."""
    try:
        # with_structured_output modele semayi zorla dayatir.
        # Model artik serbest metin degil, AnalizSonucu nesnesi doner.
        llm = model_getir(sicaklik=0.0).with_structured_output(AnalizSonucu)

        # Kod listesini elle yazmiyoruz, kurallar.py'dan cekiyoruz.
        # Boylece listeyi orada degistirince prompt kendiliginden guncellenir.
        istem = ANALIZ_PROMPT.format(
            kod_listesi=", ".join(sorted(BELIRTI_KODLARI)),
            sikayet=durum.get("sikayet", ""),
        )

        sonuc = llm.invoke(istem)

        return {
            "cihaz_tipi": sonuc.cihaz_tipi,
            "belirtiler": sonuc.belirtiler,
            # Pydantic nesnelerini sozluge cevir, cunku Durum'da
            # list[dict] olarak tanimladik. State'te ham nesne tasima.
            "olasi_sebepler": [s.model_dump() for s in sonuc.olasi_sebepler],
            "varsayimlar": sonuc.varsayimlar,
            "hata": "",
        }

    except Exception as e:
        # FAIL-SAFE: kota doldu, ag koptu veya model bozuk cevap verdi.
        # Sistemi cokertme, bos analiz dondur. triyaj bos belirti
        # listesini gorunce otomatik olarak sariya cekecek.
        return {
            "cihaz_tipi": "bilinmiyor",
            "belirtiler": [],
            "olasi_sebepler": [],
            "varsayimlar": [],
            "hata": f"Analiz yapilamadi: {e}",
        }


def triyaj(durum: Durum) -> dict:
    """Aciliyet seviyesini belirler. LLM YOK, saf kural."""
    aciliyet, bayraklar = triyaj_yap(durum.get("belirtiler", []))
    return {
        "aciliyet": aciliyet,
        "kirmizi_bayraklar": bayraklar,
    }


def servis_yonlendir(durum: Durum) -> dict:
    """Kirmizi yol. LLM YOK, sabit sablon.

    Modelden metin istemiyoruz cunku guvenlik uyarisini yumusatmasini
    istemiyoruz. Sadece tespit edilen bayraklarin adi degisken.
    """
    bayraklar = durum.get("kirmizi_bayraklar", [])

    # Kod adlarini okunabilir Turkceye cevir.
    okunabilir = [BAYRAK_METINLERI.get(b, b) for b in bayraklar]
    metin = ", ".join(okunabilir) if okunabilir else "ciddi ariza belirtisi"

    return {
        "cozum_adimlari": SERVIS_SABLONU_ADIMLARI,
        # Basligi cozum_adimlari'nin disinda tasimak yerine yanit'i
        # cikti node'unda kuracagiz, burada sadece basligi state'e
        # gecici olarak koymamak icin cikti node'u aciliyete bakacak.
    }


def cozum_uret(durum: Durum) -> dict:
    """Yesil ve sari yol. Kullanicinin kendi yapabilecegi adimlar. LLM kullanir."""
    aciliyet = durum.get("aciliyet", "sari")

    # Analiz patladiysa modele bos veri gonderip token harcamanin
    # anlami yok. Sabit bir yonlendirme dondur.
    if durum.get("hata"):
        return {
            "cozum_adimlari": [
                "Sikayetinizi su an analiz edemedim.",
                "Cihazdan yanik kokusu, duman geliyorsa veya bataryasi sismisse "
                "cihazi kullanmayi birakip servise basvurun.",
                "Boyle bir durum yoksa sikayetinizi biraz daha ayrintili yazip "
                "tekrar deneyin.",
            ]
        }

    try:
        llm = model_getir(sicaklik=0.3).with_structured_output(CozumSonucu)

        # Sebep listesini modele duz metin olarak veriyoruz.
        # Ham sozluk gondermek yerine okunabilir satirlar kurmak
        # modelin isini kolaylastirir.
        sebepler = durum.get("olasi_sebepler", [])
        sebep_metni = "\n".join(
            f"- {s['sebep']} (olasilik: {s['olasilik']}) cunku {s['gerekce']}"
            for s in sebepler
        ) or "- Belirgin bir sebep tespit edilemedi"

        varsayimlar = durum.get("varsayimlar", [])
        varsayim_metni = "\n".join(f"- {v}" for v in varsayimlar) or "- Yok"

        istem = COZUM_PROMPT.format(
            ton=TON_METINLERI.get(aciliyet, TON_METINLERI["sari"]),
            cihaz=durum.get("cihaz_tipi", "bilinmiyor"),
            sebepler=sebep_metni,
            varsayimlar=varsayim_metni,
        )

        sonuc = llm.invoke(istem)

        adimlar = list(sonuc.adimlar)
        if sonuc.uyari:
            adimlar.append(sonuc.uyari)

        return {"cozum_adimlari": adimlar}

    except Exception as e:
        return {
            "cozum_adimlari": [
                "Cozum onerisi uretilemedi, lutfen tekrar deneyin."
            ],
            "hata": f"Cozum uretilemedi: {e}",
        }


def cikti(durum: Durum) -> dict:
    """Tum dallarin birlestigi yer. State'i kullaniciya gosterilecek
    metne cevirir. Formatlama SADECE burada yapilir, boylece ileride
    Telegram veya web arayuzu eklersen tek dosyayi degistirirsin.
    """
    aciliyet = durum.get("aciliyet", "sari")
    adimlar = durum.get("cozum_adimlari", [])

    parcalar = []

    if aciliyet == "kirmizi":
        # Kirmizi yolda baslik sabit sablondan gelir.
        bayraklar = durum.get("kirmizi_bayraklar", [])
        okunabilir = [BAYRAK_METINLERI.get(b, b) for b in bayraklar]
        metin = ", ".join(okunabilir) if okunabilir else "ciddi ariza belirtisi"
        parcalar.append(SERVIS_BASLIK.format(bayraklar=metin))
    else:
        cihaz = durum.get("cihaz_tipi", "bilinmiyor")
        parcalar.append(f"Tespit edilen cihaz: {cihaz}")

        # Analizin ne dusundugunu kullaniciya da gosteriyoruz.
        # Kullanici sistemin neden bu adimlari onerdigini gorsun.
        sebepler = durum.get("olasi_sebepler", [])
        if sebepler:
            parcalar.append("\nOlasi sebepler:")
            for s in sebepler:
                parcalar.append(f"  - {s['sebep']} (olasilik: {s['olasilik']})")

        varsayimlar = durum.get("varsayimlar", [])
        if varsayimlar:
            parcalar.append("\nSu bilgileri bilmedigim icin varsaydim:")
            for v in varsayimlar:
                parcalar.append(f"  - {v}")

    if adimlar:
        parcalar.append("\nYapmaniz gerekenler:")
        for i, adim in enumerate(adimlar, start=1):
            parcalar.append(f"  {i}. {adim}")

    if aciliyet == "sari":
        parcalar.append(
            "\nBu adimlar sonuc vermezse donanim arizasi olabilir, "
            "yetkili servise basvurun."
        )

    return {"yanit": "\n".join(parcalar)}