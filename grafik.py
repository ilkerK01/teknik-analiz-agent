from langgraph.graph import END, StateGraph

from dugumler import analiz, cikti, cozum_uret, servis_yonlendir, triyaj
from durum import Durum


def yonlendirici(durum: Durum) -> str:
    return durum.get("aciliyet", "sari")


def grafik_kur(analiz_dugumu=analiz):
    """Grafigi kurar ve calistirilabilir hale getirir.

    analiz_dugumu parametresi bilincli. Varsayilan gercek analiz
    node'u, ama test ederken yerine API cagirmayan sahte bir
    fonksiyon verebilirsin. Bakiniz test_akis.py.
    """
    graf = StateGraph(Durum)

    # Node'lari kaydet. Ilk argüman grafikteki adi, ikincisi fonksiyon.
    graf.add_node("analiz", analiz_dugumu)
    graf.add_node("triyaj", triyaj)
    graf.add_node("servis_yonlendir", servis_yonlendir)
    graf.add_node("cozum_uret", cozum_uret)
    graf.add_node("cikti", cikti)

    # Giris noktasi. Trigger kutusu buna karsilik geliyor.
    graf.set_entry_point("analiz")

    # Duz kenar: analiz bitince kosulsuz triyaj calisir.
    graf.add_edge("analiz", "triyaj")

    # KOSULLU KENAR. Grafigin kalbi burasi.
    # 1. argüman: hangi node'dan sonra
    # 2. argüman: karar fonksiyonu
    # 3. argüman: fonksiyonun dondurdugu etiket -> gidilecek node
    graf.add_conditional_edges(
        "triyaj",
        yonlendirici,
        {
            "kirmizi": "servis_yonlendir",
            "sari": "cozum_uret",
            "yesil": "cozum_uret",
        },
    )

    # Iki dal da tek cikti node'unda birlesiyor.
    graf.add_edge("servis_yonlendir", "cikti")
    graf.add_edge("cozum_uret", "cikti")

    # Cikti bitince grafik biter.
    graf.add_edge("cikti", END)

    # compile() grafigi calistirilabilir bir nesneye cevirir.
    # Bu satirdan once grafik sadece bir tariftir.
    return graf.compile()