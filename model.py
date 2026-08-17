import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_ADI = "gemini-2.5-flash"


def model_getir(sicaklik: float = 0.0):
    anahtar = os.getenv("GOOGLE_API_KEY")

    if not anahtar:
        raise RuntimeError(".env dosyasinda API KEY bulunamadi")

    return ChatGoogleGenerativeAI(
        model=MODEL_ADI,
        temperature=sicaklik,
        google_api_key=anahtar,
    )
