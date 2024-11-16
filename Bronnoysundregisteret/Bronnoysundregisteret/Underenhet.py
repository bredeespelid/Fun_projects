import requests
import pandas as pd

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

# Display the dataframe
print(df)
