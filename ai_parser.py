import re


def extract_data(text):
    # datum (format: 20.05.2026 ili slično)
    date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)

    # cijena (npr 200.00 ili 200)
    price_match = re.search(r"\b\d+[.,]?\d*\b", text)

    # klijent (ovo je basic - može se kasnije poboljšati)
    client_match = re.search(r"Klijent[:\s]+([A-Za-z]+)", text)

    return {
        "datum": date_match.group(0) if date_match else None,
        "cijena": price_match.group(0) if price_match else None,
        "klijent": client_match.group(1) if client_match else None
    }