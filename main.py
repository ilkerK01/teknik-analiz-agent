from grafik import grafik_kur


def main():

    graf = grafik_kur()

    print("Teknik Servis Asistani")
    print("Cihazinizla ilgili sorunu yazin. Cikmak icin: cik\n")

    while True:
        sikayet = input("Sikayetiniz: ").strip()

        if sikayet.lower() in {"cik", "exit", "q"}:
            print("Gorusmek uzere.")
            break

        if not sikayet:
            continue


        sonuc = graf.invoke({"sikayet": sikayet})

        print("\n" + "-" * 60)
        print(sonuc["yanit"])
        print("-" * 60 + "\n")

        if sonuc.get("hata"):
            print(f"[teknik not] {sonuc['hata']}\n")


if __name__ == "__main__":
    main()