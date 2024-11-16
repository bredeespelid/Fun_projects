import requests
import csv
from io import StringIO
import sys
import os
import openai

def increase_csv_field_limit():
    """
    Øker CSV-feltgrensen for å håndtere store CSV-felt.
    """
    max_int = sys.maxsize
    decrement = True
    while decrement:
        try:
            csv.field_size_limit(max_int)
            decrement = False
        except OverflowError:
            max_int = int(max_int / 10)
    return max_int

increase_csv_field_limit()

# Sett OpenAI API-nøkkel fra miljøvariabler
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("Feil: OPENAI_API_KEY er ikke satt som en miljøvariabel.")
    sys.exit(1)

def generate_market_analysis(prompt):
    """
    Generer en markedsanalyse ved hjelp av OpenAI's ChatGPT.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du er en markedsanalysespesialist."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Juster etter behov
        )
        analysis = response['choices'][0]['message']['content'].strip()
        return analysis
    except Exception as e:
        print(f"Feil under generering av markedsanalyse: {e}")
        return None

def recommend_business_codes(analysis, business_codes):
    """
    Anbefal næringskoder basert på markedsanalysen ved hjelp av ChatGPT.
    """
    try:
        # Lag en prompt som ber ChatGPT om å anbefale næringskoder basert på analysen
        prompt = (
            "Basert på følgende markedsanalyse for kaffebransjen, velg de mest relevante næringskodene fra listen nedenfor.\n\n"
            f"Markedsanalyse:\n{analysis}\n\n"
            "Næringskoder:\n"
        )
        
        # Begrens antall kodeeksempler for å unngå å overskride token-grensen
        sample_codes = business_codes[:50]  # Juster antall etter behov
        
        for code in sample_codes:
            prompt += f"{code['code']} | {code['name']}\n"
        
        prompt += "\nVennligst oppgi de næringskodene som best passer til analysen ovenfor."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du er en ekspert på å matche forretningsbeskrivelser med norsk næringskode."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150  # Juster etter behov
        )
        recommendations = response['choices'][0]['message']['content'].strip()
        return recommendations
    except Exception as e:
        print(f"Feil under anbefaling av næringskoder: {e}")
        return None

def main():
    """
    Hovedfunksjon som genererer markedsanalyse og anbefaler næringskoder.
    """
    # Brukeren ønsker en markedsanalyse for kaffebransjen
    user_input = "Lag en markedsanalyse for kaffebransjen i Norge."

    print("Genererer markedsanalyse for kaffebransjen...")
    market_analysis = generate_market_analysis(user_input)

    if not market_analysis:
        print("Kunne ikke generere markedsanalyse.")
        return

    print("\nMarkedsanalyse:\n")
    print(market_analysis)

    # Hent næringskoder fra SSB API
    url = "https://data.ssb.no/api/klass/v1/classifications/6/codesAt"
    params = {
        "date": "2024-10-03",
        "language": "nb",
        "csvSeparator": ";"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("\nAPI-forespørsel vellykket. Henter næringskoder...")
        
        csv_content = StringIO(response.text)
        csv_reader = csv.DictReader(csv_content, delimiter=';')
        
        business_codes = []
        for row in csv_reader:
            if 'code' in row and 'name' in row:
                business_codes.append({'code': row['code'], 'name': row['name']})
        
        print(f"Totalt hentet næringskoder: {len(business_codes)}")
    else:
        print(f"Feil: Kunne ikke hente data. Statuskode: {response.status_code}")
        print("Responsinnhold:")
        print(response.text)
        return

    print("\nAnbefaler relevante næringskoder basert på markedsanalysen...")
    recommended_codes = recommend_business_codes(market_analysis, business_codes)

    if recommended_codes:
        print("\nAnbefalte Næringskoder:")
        print(recommended_codes)
    else:
        print("Kunne ikke anbefale næringskoder.")

if __name__ == "__main__":
    main()
