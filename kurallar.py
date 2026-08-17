BELIRTI_KODLARI = frozenset(
    {
        "guc_yok",
        "sarjli_ama_acilmiyor",
        "yanik_kokusu",
        "duman",
        "batarya_sismis",
        "sivi_temasi",
        "elektrik_carpmasi",
        "disk_tikirtisi",
        "fiziksel_hasar",
        "ekran_kirik",
        "ani_kapanma",
        "asiri_isinma",
        "bip_sesi",
        "ses_yok",
        "ses_cizirtili",
        "mikrofon_calismiyor",
        "wifi_yok",
        "yavas_calisiyor",
        "mavi_ekran",
        "acilista_donuyor",
        "diger",
    }
)

KIRMIZI_BAYRAKLAR = frozenset(
    {
        "yanik_kokusu",
        "duman",
        "batarya_sismis",
        "sivi_temasi",
        "elektrik_carpmasi",
        "sarjli_ama_acilmiyor",
        "disk_tikirtisi",
    }
)

SARI_BAYRAKLAR = frozenset(
    {
        "fiziksel_hasar",
        "ekran_kirik",
        "ani_kapanma",
        "asiri_isinma",
        "bip_sesi",
    }
)

BAYRAK_METINLERI = {
    "yanik_kokusu": "yanik kokusu",
    "duman": "duman",
    "batarya_sismis": "sismis batarya",
    "sivi_temasi": "cihaza sivi temasi",
    "elektrik_carpmasi": "govdede elektrik hissi",
    "sarjli_ama_acilmiyor": "sarji oldugu halde acilmama",
    "disk_tikirtisi": "sabit diskten tikirti sesi",
}


def triyaj_yap(belirtiler: list[str]) -> tuple[str, list[str]]:
    temiz = set(b for b in belirtiler if b in BELIRTI_KODLARI)
    kirmizi = sorted(temiz & KIRMIZI_BAYRAKLAR)
    if kirmizi:
        return "kirmizi", kirmizi

    if not temiz:
        return "sari", []

    if temiz & SARI_BAYRAKLAR:
        return "sari", []

    return "yesil", []


# Geriye dönuk uyumluluk: eski ismi kullanan yerler varsa bozmayalim.
triyaj_uygula = triyaj_yap


if __name__ == "__main__":
    ornekler = [
        ["ses_yok", "wifi_yok"],
        ["sarjli_ama_acilmiyor"],
        ["batarya_sismis", "asiri_isinma"],
        ["ani_kapanma"],
        [],
        ["uydurma_kod"],
    ]
    for ornek in ornekler:
        print(ornek, "->", triyaj_yap(ornek))
