from typing import TypedDict


class Durum(TypedDict, total=False):
    # Kullanici girdisi
    sikayet: str

    # Analiz node'u
    cihaz_tipi: str
    belirtiler: list[str]
    olasi_sebepler: list[dict]
    varsayimlar: list[str]
    hata: str

    # Triyaj node'u
    kirmizi_bayraklar: list[str]
    aciliyet: str

    # Cikti
    cozum_adimlari: list[str]
    yanit: str
