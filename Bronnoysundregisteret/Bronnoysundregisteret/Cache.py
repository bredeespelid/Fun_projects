import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time

# Input parametere
KOMMUNE_NUMMER = "0301"  # Oslo kommune
NAERINGSKODER = ["47.24", "47.25", "47.26"]  # Butikkhandel med brød og konditorvarer, drikkevarer, tobakksvarer
API_URL = "https://data.brreg.no/enhetsregisteret/api/underenheter"
REGNSKAPS_API_URL = "https://data.brreg.no/regnskapsregisteret/regnskap/"
REGNSKAPSTYPE = "SELSKAP"
AAR = 2023
BATCH_SIZE = 50
RESULTAT_FIL = r"C:\Users\brede\OneDrive\Skrivebord\Ny mappe\underenheter_oslo_med_driftsresultat.csv"

# Funksjoner forblir uendret
def get_company_financial_data(orgnr, year, regnskapstype=REGNSKAPSTYPE):
    url = f"{REGNSKAPS_API_URL}{orgnr}"
    params = {
        'år': year,
        'regnskapstype': regnskapstype
    }
    
    headers = {'accept': 'application/xml'}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.text
    else:
        return f"Feil: {response.status_code}, melding: {response.text}"

def extract_orgnr_and_driftsresultat(xml_data):
    root = ET.fromstring(xml_data)
    
    orgnr = root.find('.//virksomhet/organisasjonsnummer').text if root.find('.//virksomhet/organisasjonsnummer') is not None else "N/A"
    
    driftsresultat = root.find('.//driftsresultat/driftsresultat').text if root.find('.//driftsresultat/driftsresultat') is not None else "N/A"
    
    return orgnr, driftsresultat

# Hent underenheter
all_units = []

for kode in NAERINGSKODER:
    page = 0
    params = {
        "beliggenhetsadresse.kommunenummer": KOMMUNE_NUMMER,
        "naeringskode": kode,
        "size": 1000,
        "page": page
    }
    
    while True:
        time.sleep(1)
        response = requests.get(API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            units = data.get('_embedded', {}).get('underenheter', [])
            
            if not units:
                break
            
            all_units.extend(units)
            page += 1
            params["page"] = page
        else:
            print(f"Feil ved forespørsel for næringskode {kode}: {response.status_code}")
            break

    print(f"Hentet data for næringskode {kode}")

print(f"Totalt antall underenheter hentet: {len(all_units)}")

df = pd.DataFrame([{
    'Organisasjonsnummer': unit.get('organisasjonsnummer', ''),
    'Navn': unit.get('navn', ''),
    'Antall Ansatte': unit.get('antallAnsatte', ''),
    'Kommune': unit.get('beliggenhetsadresse', {}).get('kommune', ''),
    'Adresse': unit.get('beliggenhetsadresse', {}).get('adresse', [''])[0],
    'Overordnet Enhet': unit.get('overordnetEnhet', ''),
    'Næringskode': unit.get('naeringskode', {}).get('kode', '')
} for unit in all_units])

# Opprett en cache for driftsresultater
driftsresultat_cache = {}

driftsresultater = []

for i in range(0, len(df), BATCH_SIZE):
    batch = df.iloc[i:i+BATCH_SIZE]
    
    for index, row in batch.iterrows():
        overordnet_enhet = row['Overordnet Enhet']
        
        if overordnet_enhet:
            if overordnet_enhet in driftsresultat_cache:
                driftsresultater.append(driftsresultat_cache[overordnet_enhet])
            else:
                xml_data = get_company_financial_data(overordnet_enhet, AAR)
                
                if not xml_data.startswith("Feil"):
                    orgnr, driftsresultat = extract_orgnr_and_driftsresultat(xml_data)
                    
                    if driftsresultat != "N/A":
                        driftsresultat_cache[overordnet_enhet] = driftsresultat
                        driftsresultater.append(driftsresultat)
                    else:
                        driftsresultat_cache[overordnet_enhet] = "Ikke tilgjengelig"
                        driftsresultater.append("Ikke tilgjengelig")
                else:
                    driftsresultat_cache[overordnet_enhet] = "Feil ved henting"
                    driftsresultater.append("Feil ved henting")
                
                time.sleep(0.5)  # Pause kun når vi faktisk henter nye data
        else:
            driftsresultater.append("Ingen overordnet enhet")
    
    print(f"Behandlet {len(driftsresultater)} av {len(df)} enheter")

df['Driftsresultat Overordnet Enhet'] = driftsresultater

df.to_csv(RESULTAT_FIL, index=False)

print(f"Data lagret til {RESULTAT_FIL}")
