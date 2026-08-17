from typing import Literal

from pydantic import BaseModel, Field


class Sebep(BaseModel):
    sebep: str = Field(description="Arizanin olasi teknik sebebi, tek cumle, kisa ve oz.")
    olasilik: Literal["yuksek", "orta", "dusuk"] = Field(
        description="Gercekten bu sebepten kaynaklanma olasiligi"
    )
    gerekce: str = Field(
        description="Bu sebepten neden suphe duydugun. Kisa ve oz, bir iki cumleyi gecmez."
    )


class AnalizSonucu(BaseModel):
    cihaz_tipi: Literal["masaustu", "laptop", "bilinmiyor"] = Field(
        description="Sikayet sonucu tahmin edilen cihaz tipi, tahmin edilmiyorsa bilinmiyor olarak isaretlenir"
    )
    belirtiler: list[str] = Field(
        description="Sadece verilen belirti kodu listesinden secilmis kodlar"
    )
    olasi_sebepler: list[Sebep] = Field(
        description="En olasi 2 ile 4 sebep, olasiligi yuksekten dusuge dogru siralidir."
    )
    varsayimlar: list[str] = Field(
        description="Sikayette eksik olan ve varsaymak zorunda oldugun bilgiler."
    )


class CozumSonucu(BaseModel):
    adimlar: list[str] = Field(
        description="Kullanicinin sikayeti cozmek icin kendi yapabilecegi adimlar, en basitten baslayarak"
    )
    uyari: str = Field(
        description="Adimlar ise yaramazsa ne yapmasi gerektigini tek cumle ile aciklanir"
    )
