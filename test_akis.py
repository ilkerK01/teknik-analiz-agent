from grafik import grafik_kur
import dugumler


def sahte_analiz_kirmizi(durum):
    """Gercek analiz node'unun yerine gecer. LLM cagirmaz."""
    return {
        "cihaz_tipi": "laptop",
        "belirtiler": ["batarya_sismis", "asiri_isinma"],
        "olasi_sebepler": [
            {"sebep": "Batarya sisme", "olasilik": "yuksek", "gerekce": "test"}
        ],
        "varsayimlar": [],
        "hata": "",
    }


def sahte_analiz_yesil(durum):
    """Yesil yolu test eder."""
    return {
        "cihaz_tipi": "laptop",
        "belirtiler": ["ses_yok"],
        "olasi_sebepler": [
            {
                "sebep": "Yanlis ses cikis aygiti secili",
                "olasilik": "yuksek",
                "gerekce": "test",
            }
        ],
        "varsayimlar": ["Kulaklik takili olup olmadigi bilinmiyor"],
        "hata": "",
    }


class SahteLLM:
    def __init__(self, schema):
        self.schema = schema

    def invoke(self, istem):
        if self.schema.__name__ == "CozumSonucu":
            return self.schema(
                adimlar=[
                    "Ses aygiti ayarlarini kontrol edin.",
                    "Cihazi sessize alinip alinmadigini kontrol edin.",
                ],
                uyari="Sorun devam ederse yetkili servise basvurun.",
            )

        return self.schema(
            cihaz_tipi="bilinmiyor",
            belirtiler=[],
            olasi_sebepler=[],
            varsayimlar=[],
        )


class SahteModel:
    def with_structured_output(self, schema):
        return SahteLLM(schema)


def sahte_model_getir(sicaklik=0.0):
    return SahteModel()


if __name__ == "__main__":
    # LLM yerine sahte model kullan.
    dugumler.model_getir = sahte_model_getir

    print("=" * 60)
    print("KIRMIZI YOL TESTI")
    print("=" * 60)
    graf = grafik_kur(analiz_dugumu=sahte_analiz_kirmizi)
    sonuc = graf.invoke({"sikayet": "test"})
    print(sonuc["yanit"])
    print("\nAciliyet:", sonuc["aciliyet"])

    print("\n" + "=" * 60)
    print("YESIL YOL TESTI")
    print("=" * 60)
    graf = grafik_kur(analiz_dugumu=sahte_analiz_yesil)
    sonuc = graf.invoke({"sikayet": "test"})
    print(sonuc["yanit"])
    print("\nAciliyet:", sonuc["aciliyet"])
