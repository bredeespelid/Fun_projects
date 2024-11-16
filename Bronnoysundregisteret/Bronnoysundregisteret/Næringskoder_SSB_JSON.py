import requests
import sys

def increase_field_limit():
    max_int = sys.maxsize
    decrement = True
    while decrement:
        try:
            sys.maxsize = max_int
            decrement = False
        except OverflowError:
            max_int = int(max_int / 10)
    return max_int

increase_field_limit()

url = "https://data.ssb.no/api/klass/v1/classifications/6/codesAt"
params = {
    "date": "2024-10-03",
    "language": "nb",
    "format": "json"  # Endre til JSON format
}

response = requests.get(url, params=params)

if response.status_code == 200:
    print("API-forespørsel vellykket")
    
    # Parse responsen som JSON
    data = response.json()
    
    # Sjekk om data er en liste eller en dict
    if isinstance(data, list):
        print("Innhold av JSON-respons (første 2 elementer):")
        print(data[:2])  # Skriv ut de første 2 postene av JSON hvis det er en liste
    else:
        print("Innhold av JSON-respons (hele):")
        print(data)  # Skriv ut hele objektet hvis det er en dict
    
    print("\nNæringskoder:")
    print("Kode | Navn")
    print("-" * 50)
    
    # Loop gjennom JSON-dataene for å skrive ut kode og navn hvis det er en liste
    if isinstance(data, list):
        for item in data:
            if 'code' in item and 'name' in item:
                print(f"{item['code']} | {item['name']}")
            else:
                print(f"Uventet format: {item}")
    else:
        print(f"Uventet JSON-format: {type(data)}")
else:
    print(f"Feil: Kunne ikke hente data. Statuskode: {response.status_code}")
    print("Responsinnhold:")
    print(response.text)
