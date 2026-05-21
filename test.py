from datetime import datetime

ime = input("Unesi ime klijenta: ")
cijena = float(input("Unesi cijenu: "))

pdv = cijena * 0.17
ukupno = cijena + pdv

datum = datetime.now().strftime("%d.%m.%Y")

faktura = f"""
===== FAKTURA =====
Datum: {datum}
Klijent: {ime}
Cijena: {cijena}
PDV (17%): {pdv}
UKUPNO: {ukupno}
"""

print(faktura)

with open("faktura.txt", "a", encoding="utf-8") as file:
    file.write(faktura + "\n\n")