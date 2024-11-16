import requests
import pandas as pd
import xml.etree.ElementTree as ET

# Funksjon for å hente regnskapsdata fra API
def get_company_financial_data(orgnr, year, regnskapstype="SELSKAP"):
    url = f"https://data.brreg.no/regnskapsregisteret/regnskap/{orgnr}"
    params = {
        'år': year,
        'regnskapstype': regnskapstype
    }
    
    headers = {'accept': 'application/xml'}
    
    # Send forespørselen til API-et
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.text  # Returner XML-data
    else:
        return f"Feil: {response.status_code}, melding: {response.text}"

# Funksjon for å hente informasjon om den overordnede enheten
def get_company_name(orgnr):
    url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('navn', "N/A")
    else:
        return f"Feil ved henting: {response.status_code}"

# Funksjon for å trekke ut organisasjonsnummer og driftsresultat fra XML
def extract_orgnr_and_driftsresultat(xml_data):
    root = ET.fromstring(xml_data)
    
    # Hent organisasjonsnummer
    orgnr = root.find('.//virksomhet/organisasjonsnummer').text if root.find('.//virksomhet/organisasjonsnummer') is not None else "N/A"
    
    # Hent driftsresultat
    driftsresultat = root.find('.//driftsresultat/driftsresultat').text if root.find('.//driftsresultat/driftsresultat') is not None else "N/A"
    
    return orgnr, driftsresultat

# API URL
url = "https://data.brreg.no/enhetsregisteret/api/underenheter"

# Parameters for the request
params = {
    "beliggenhetsadresse.kommunenummer": "0301",  # Oslo kommune
    "naeringskode": "47.24",  # Butikkhandel med brød og konditorvarer
    "size": 100,  # Number of results per page
    "page": 0  # Starting page
}

# Initialize an empty list to store all results
all_units = []

# Loop through pages
while True:
    # Send the GET request
    response = requests.get(url, params=params)
    
    # If the request is successful
    if response.status_code == 200:
        # Extract the relevant data from the response
        data = response.json()
        units = data.get('_embedded', {}).get('underenheter', [])
        
        # Append the units from this page to the all_units list
        all_units.extend(units)
        
        # Check if there is another page
        if "next" in data.get('_links', {}):
            params["page"] += 1  # Move to the next page
        else:
            break  # No more pages, exit the loop
    else:
        print(f"Feil ved forespørsel: {response.status_code}")
        break

# Convert the list of all units into a dataframe
df = pd.DataFrame([{
    'Organisasjonsnummer': unit.get('organisasjonsnummer', ''),
    'Navn': unit.get('navn', ''),
    'Antall Ansatte': unit.get('antallAnsatte', ''),
    'Kommune': unit.get('beliggenhetsadresse', {}).get('kommune', ''),
    'Adresse': unit.get('beliggenhetsadresse', {}).get('adresse', [''])[0],
    'Overordnet Enhet': unit.get('overordnetEnhet', '')  # Overordnet enhet (parent unit)
} for unit in all_units])

# År for regnskapsdata
år = 2023

# Hent driftsresultat for overordnet enhet og navn på overordnet enhet
driftsresultater = []
overordnet_navn = []

for index, row in df.iterrows():
    overordnet_enhet = row['Overordnet Enhet']
    
    # Sjekk om overordnet enhet eksisterer
    if overordnet_enhet:
        # Hent driftsresultat
        xml_data = get_company_financial_data(overordnet_enhet, år)
        
        if not xml_data.startswith("Feil"):
            orgnr, driftsresultat = extract_orgnr_and_driftsresultat(xml_data)
            
            if driftsresultat != "N/A":
                driftsresultater.append(driftsresultat)
            else:
                driftsresultater.append("Ikke tilgjengelig")
        else:
            driftsresultater.append("Feil ved henting")
        
        # Hent navn på overordnet enhet
        overordnet_navn.append(get_company_name(overordnet_enhet))
    else:
        driftsresultater.append("Ingen overordnet enhet")
        overordnet_navn.append("Ingen overordnet enhet")

# Legg til driftsresultat og navn på overordnet enhet som nye kolonner i dataframe
df['Driftsresultat Overordnet Enhet'] = driftsresultater
df['Overordnet Enhet Navn'] = overordnet_navn

# Lagre dataframe til CSV
file_path = r"C:\Users\brede\OneDrive\Skrivebord\Ny mappe\underenheter_oslo_med_driftsresultat_og_navn.csv"
df.to_csv(file_path, index=False)

print(f"Data lagret til {file_path}")
