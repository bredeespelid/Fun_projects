import asyncio
import aiohttp
import pandas as pd
import xml.etree.ElementTree as ET
import json
from aiohttp import ClientSession
from asyncio import Semaphore
import os
import nest_asyncio
import numpy as np

# Aktiver nest_asyncio hvis en event loop allerede kjører
try:
    asyncio.get_running_loop()
    nest_asyncio.apply()
except RuntimeError:
    pass

# Input parametere
KOMMUNE_NUMMER = ""  # Empty string for no specific kommune
NAERINGSKODER = ["10.710", "47.241"]  # Liste av næringskoder
API_URL = "https://data.brreg.no/enhetsregisteret/api/underenheter"
ENHET_API_URL = "https://data.brreg.no/enhetsregisteret/api/enheter/"
REGNSKAPS_API_URL = "https://data.brreg.no/regnskapsregisteret/regnskap/"
REGNSKAPSTYPE = "SELSKAP"
AAR = 2023
RESULTAT_FIL = r"Analyse.csv"
CACHE_FINANSIELL_FIL = 'finansiell_cache.json'
CACHE_NAVNFLIL = 'navn_cache.json'
MAX_CONCURRENT_REQUESTS = 10

# Global variable to store the DataFrame
global_df = None

# Asynkrone funksjoner
async def fetch(session: ClientSession, url: str, params=None, headers=None):
    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                if headers and 'application/json' in headers.get('accept', ''):
                    return await response.json()
                else:
                    return await response.text()
            else:
                return f"Feil: {response.status}, melding: {await response.text()}"
    except Exception as e:
        return f"Unntak: {str(e)}"

async def get_company_financial_data(session: ClientSession, orgnr: str, year: int, regnskapstype=REGNSKAPSTYPE):
    url = f"{REGNSKAPS_API_URL}{orgnr}"
    params = {'år': year, 'regnskapstype': regnskapstype}
    headers = {'accept': 'application/xml'}
    return await fetch(session, url, params=params, headers=headers)

async def get_enhet_details(session: ClientSession, orgnr: str):
    url = f"{ENHET_API_URL}{orgnr}"
    headers = {'accept': 'application/json'}
    data = await fetch(session, url, headers=headers)

    if isinstance(data, dict) and "error" not in data:
        vedtektsfestet_formaal = data.get('vedtektsfestetFormaal', [''])
        aktivitet = data.get('aktivitet', [''])
        navn = data.get('navn', '')
        return vedtektsfestet_formaal, aktivitet, navn
    else:
        return ["Feil ved henting"], ["Feil ved henting"], "Feil ved henting"

async def get_total_underenheter(session: ClientSession, orgnr: str):
    params = {"overordnetEnhet": orgnr}
    data = await fetch(session, API_URL, params=params, headers={'accept': 'application/json'})
    if isinstance(data, dict):
        return data.get("page", {}).get("totalElements", 0)
    return 0

def extract_financial_data(xml_data: str):
    try:
        root = ET.fromstring(xml_data)
        orgnr = root.find('.//virksomhet/organisasjonsnummer').text if root.find('.//virksomhet/organisasjonsnummer') is not None else ""
        driftsresultat = root.find('.//driftsresultat/driftsresultat').text if root.find('.//driftsresultat/driftsresultat') is not None else ""
        sum_driftsinntekter = root.find('.//driftsinntekter/sumDriftsinntekter').text if root.find('.//driftsinntekter/sumDriftsinntekter') is not None else ""
        sum_driftskostnad = root.find('.//driftskostnad/sumDriftskostnad').text if root.find('.//driftskostnad/sumDriftskostnad') is not None else ""
        finansinntekter = root.find('.//finansresultat/finansinntekt/sumFinansinntekter').text if root.find('.//finansresultat/finansinntekt/sumFinansinntekter') is not None else ""
        egenkapital = root.find('.//egenkapitalGjeld/egenkapital/sumEgenkapital').text if root.find('.//egenkapitalGjeld/egenkapital/sumEgenkapital') is not None else ""
        gjeld = root.find('.//egenkapitalGjeld/gjeldOversikt/sumGjeld').text if root.find('.//egenkapitalGjeld/gjeldOversikt/sumGjeld') is not None else ""
        return orgnr, driftsresultat, sum_driftsinntekter, sum_driftskostnad, finansinntekter, egenkapital, gjeld
    except ET.ParseError:
        return "", "Ugyldig XML", "Ugyldig XML", "Ugyldig XML", "Ugyldig XML", "Ugyldig XML", "Ugyldig XML"

async def process_orgnr(orgnr: str):
    async with sem:
        driftsresultat = sum_driftsinntekter = sum_driftskostnad = finansinntekter = egenkapital = gjeld = "Ingen overordnet enhet"
        vedtektsfestet_formaal, aktivitet, overordnet_navn = ["Ingen overordnet enhet"], ["Ingen overordnet enhet"], "Ingen overordnet enhet"
        total_underenheter = 0

        if orgnr:
            if orgnr in finansiell_cache:
                driftsresultat, sum_driftsinntekter, sum_driftskostnad, finansinntekter, egenkapital, gjeld = finansiell_cache[orgnr]
            else:
                xml_data = await get_company_financial_data(session, orgnr, AAR)
                if not (isinstance(xml_data, str) and (xml_data.startswith("Feil") or xml_data.startswith("Unntak"))):
                    _, drifts, sum_innt, sum_kost, fin_innt, egen_kap, gje = extract_financial_data(xml_data)
                    driftsresultat = drifts if drifts != "" else "Ikke tilgjengelig"
                    sum_driftsinntekter = sum_innt if sum_innt != "" else "Ikke tilgjengelig"
                    sum_driftskostnad = sum_kost if sum_kost != "" else "Ikke tilgjengelig"
                    finansinntekter = fin_innt if fin_innt != "" else "Ikke tilgjengelig"
                    egenkapital = egen_kap if egen_kap != "" else "Ikke tilgjengelig"
                    gjeld = gje if gje != "" else "Ikke tilgjengelig"
                    finansiell_cache[orgnr] = (driftsresultat, sum_driftsinntekter, sum_driftskostnad, finansinntekter, egenkapital, gjeld)
                else:
                    driftsresultat = sum_driftsinntekter = sum_driftskostnad = finansinntekter = egenkapital = gjeld = "Feil ved henting"
                    finansiell_cache[orgnr] = (driftsresultat, sum_driftsinntekter, sum_driftskostnad, finansinntekter, egenkapital, gjeld)

            vedtektsfestet_formaal, aktivitet, overordnet_navn = await get_enhet_details(session, orgnr)
            total_underenheter = await get_total_underenheter(session, orgnr)

        return orgnr, driftsresultat, sum_driftsinntekter, sum_driftskostnad, finansinntekter, egenkapital, gjeld, vedtektsfestet_formaal, aktivitet, overordnet_navn, total_underenheter

async def main():
    global sem, finansiell_cache, session

    # Laste inn cache
    if os.path.exists(CACHE_FINANSIELL_FIL):
        with open(CACHE_FINANSIELL_FIL, 'r', encoding='utf-8') as f:
            finansiell_cache = json.load(f)
    else:
        finansiell_cache = {}

    if os.path.exists(CACHE_NAVNFLIL):
        with open(CACHE_NAVNFLIL, 'r', encoding='utf-8') as f:
            navn_cache = json.load(f)
    else:
        navn_cache = {}

    sem = Semaphore(MAX_CONCURRENT_REQUESTS)

    async with ClientSession() as session:
        # Hent underenheter
        all_units = []
        for kode in NAERINGSKODER:
            page = 0
            params = {
                "naeringskode": kode,
                "size": 1000,
                "page": page
            }
            
            if KOMMUNE_NUMMER:
                params["beliggenhetsadresse.kommunenummer"] = KOMMUNE_NUMMER

            while True:
                await asyncio.sleep(0.1)
                response = await fetch(session, API_URL, params=params, headers={'accept': 'application/json'})
                if isinstance(response, dict):
                    units = response.get('_embedded', {}).get('underenheter', [])
                else:
                    print(f"Feil ved henting av underenheter for næringskode {kode}: {response}")
                    break

                if not units:
                    break

                all_units.extend(units)
                page += 1
                params["page"] = page

        print(f"Totalt antall underenheter hentet: {len(all_units)}")

        # Filtrer enheter basert på spesifiserte næringskoder
        filtered_units = [unit for unit in all_units if all(code.get('kode', '').startswith(tuple(NAERINGSKODER)) for code in [unit.get('naeringskode1', {}), unit.get('naeringskode2', {}), unit.get('naeringskode3', {})] if code)]

        print(f"Antall enheter etter filtrering: {len(filtered_units)}")

        # Opprett DataFrame med filtrerte enheter
        df_data = []
        for unit in filtered_units:
            try:
                df_data.append({
                    'Underenhet organisasjonsnummer': unit.get('organisasjonsnummer', ''),
                    'Navn Underenhet': unit.get('navn', ''),
                    'Antall Ansatte Underenhet': unit.get('antallAnsatte', ''),
                    'Næringskoder Underenhet': ', '.join([code.get('kode', '') for code in [unit.get('naeringskode1', {}), unit.get('naeringskode2', {}), unit.get('naeringskode3', {})] if code]),
                    'Kommune Underenhet': unit.get('beliggenhetsadresse', {}).get('kommune', ''),
                    'Adresse Underenhet': unit.get('beliggenhetsadresse', {}).get('adresse', [''])[0] if unit.get('beliggenhetsadresse', {}).get('adresse') else '',
                    'Overordnet Enhet organisasjonsnummer': unit.get('overordnetEnhet', '')
                })
            except Exception as e:
                print(f"Error processing unit: {unit.get('organisasjonsnummer', 'Unknown')}. Error: {str(e)}")
      

        df = pd.DataFrame(df_data)

        # Identifiser unike Overordnet Enhet orgnr
        unique_orgnr = df['Overordnet Enhet organisasjonsnummer'].dropna().unique()

        # Opprett oppgaver for å hente detaljer om Overordnet Enhet
        tasks = [process_orgnr(orgnr) for orgnr in unique_orgnr if orgnr]

        # Kjør oppgaver
        print("Starter parallell henting av enhetsdetaljer...")
        results = await asyncio.gather(*tasks)
        print("Fullført henting av enhetsdetaljer.")

        # Lag mapper for rask oppslag
        drifts_map = {orgnr: drifts for orgnr, drifts, _, _, _, _, _, _, _, _, _ in results}
        sum_innt_map = {orgnr: sum_innt for orgnr, _, sum_innt, _, _, _, _, _, _, _, _ in results}
        sum_kost_map = {orgnr: sum_kost for orgnr, _, _, sum_kost, _, _, _, _, _, _, _ in results}
        finansinntekter_map = {orgnr: fin_innt for orgnr, _, _, _, fin_innt, _, _, _, _, _, _ in results}
        egenkapital_map = {orgnr: egen_kap for orgnr, _, _, _, _, egen_kap, _, _, _, _, _ in results}
        gjeld_map = {orgnr: gjeld for orgnr, _, _, _, _, _, gjeld, _, _, _, _ in results}
        formaal_map = {orgnr: formaal for orgnr, _, _, _, _, _, _, formaal, _, _, _ in results}
        aktivitet_map = {orgnr: aktivitet for orgnr, _, _, _, _, _, _, _, aktivitet, _, _ in results}
        navn_map = {orgnr: navn for orgnr, _, _, _, _, _, _, _, _, navn, _ in results}
        total_underenheter_map = {orgnr: total for orgnr, _, _, _, _, _, _, _, _, _, total in results}

        # Map detaljer til DataFrame som nye kolonner
        df['Overordnet Enhet Navn'] = df['Overordnet Enhet organisasjonsnummer'].map(navn_map).fillna("")
        df['Vedtektsfestet Formål Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(formaal_map).apply(lambda x: ', '.join(x))
        df['Aktivitet Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(aktivitet_map).apply(lambda x: ', '.join(x))
        df['Sum Driftsinntekter Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(sum_innt_map).replace({"Feil ved henting": "", "Ikke tilgjengelig": ""})
        df['Sum Driftskostnad Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(sum_kost_map).replace({"Feil ved henting": "", "Ikke tilgjengelig": ""})
        df['Driftsresultat Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(drifts_map).replace({"Feil ved henting": "", "Ikke tilgjengelig": ""})
        df['Finansinntekter Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(finansinntekter_map).replace({"Feil ved henting": "", "Ikke tilgjengelig": ""})
        df['Egenkapital Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(egenkapital_map).replace({"Feil ved henting": "", "Ikke tilgjengelig": ""})
        df['Gjeld Overordnet Enhet'] = df['Overordnet Enhet organisasjonsnummer'].map(gjeld_map).replace({"Feil ved henting": "", "Ikke tilgjengelig": ""})
  
        # Legg til kolonnen 'ID_SammeOE' for å gruppere underenheter med samme overordnet enhet
        df['ID_SammeOE'] = df.groupby('Overordnet Enhet organisasjonsnummer').ngroup()

        # Legg til kolonnen 'Flere_underenheter'
        df['Flere_underenheter'] = df['Overordnet Enhet organisasjonsnummer'].map(df.groupby('Overordnet Enhet organisasjonsnummer').size() > 1).map({True: 'Ja', False: 'Nei'})
        # Legg til kolonnen 'Antall underenheter'

        df['Antal underenheter'] = df.groupby('Overordnet Enhet organisasjonsnummer')['ID_SammeOE'].transform('count')
        df['Total underenheter'] = df['Overordnet Enhet organisasjonsnummer'].map(total_underenheter_map) 
        df[' Underenheter %'] = round((df['Antal underenheter']/df['Total underenheter'])*100)
        # Konverter 'Næringskoder Underenhet' til tekst
        df['Næringskoder Underenhet'] = df['Næringskoder Underenhet'].astype(str)


        kolonner_til_heltall = [
            'Sum Driftsinntekter Overordnet Enhet',
            'Sum Driftskostnad Overordnet Enhet',
            'Driftsresultat Overordnet Enhet',
            'Finansinntekter Overordnet Enhet',
            'Egenkapital Overordnet Enhet',
            'Gjeld Overordnet Enhet'
        ]

        for kolonne in kolonner_til_heltall:
            df[kolonne] = df[kolonne].apply(lambda x: int(float(x)) if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('-', '').replace('.', '').isdigit()) else '')
            
            # Remove .00 from the end of numbers, including negative numbers
            df[kolonne] = df[kolonne].apply(lambda x: f"{int(float(x))}" if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('-', '').replace('.', '').isdigit()) else '')
        
        
                # Konverter kolonner til numeriske verdier
        columns_to_convert = ['Sum Driftsinntekter Overordnet Enhet', 'Finansinntekter Overordnet Enhet', 
                              'Egenkapital Overordnet Enhet', 'Gjeld Overordnet Enhet']

        for col in columns_to_convert:
            df[col] = pd.to_numeric(df[col].replace('', '0').replace('Ikke tilgjengelig', '0'), errors='coerce')

        # Konverter finansielle kolonner til numeriske verdier
        for kolonne in kolonner_til_heltall:
            df[kolonne] = pd.to_numeric(df[kolonne], errors='coerce')

        # Beregn TKR
        df['TKR'] = ((df['Sum Driftsinntekter Overordnet Enhet'] + df['Driftsresultat Overordnet Enhet']) / 
                    (df['Sum Driftsinntekter Overordnet Enhet'] + df['Sum Driftskostnad Overordnet Enhet']))

        # Håndter uendelige verdier og NaN
        df['TKR'] = df['TKR'].replace([np.inf, -np.inf], np.nan)

        # Rund av TKR til to desimaler
        df['TKR'] = df['TKR'].round(2)

        # Vis antall negative TKR-verdier
        print(f"Antall negative TKR-verdier: {(df['TKR'] < 0).sum()}")

        # Lagre oppdatert cache
        with open(CACHE_FINANSIELL_FIL, 'w', encoding='utf-8') as f:
            json.dump(finansiell_cache, f, ensure_ascii=False, indent=2)

        return df

if __name__ == "__main__":
    global_df = asyncio.run(main())
    print("Data has been fetched and stored in the 'global_df' variable.")
    print(f"Number of rows in the DataFrame: {len(global_df)}")

    # Implementer filtreringen
    filtered_df = global_df[global_df['TKR'].notna() & (global_df[' Underenheter %'] > 80)]
    print(f"Number of rows after filtering: {len(filtered_df)}")

    # Lagre filtrerte data til CSV
    filtered_df.to_csv(RESULTAT_FIL, index=False, encoding='utf-8-sig')
    print(f"Filtered data saved to {RESULTAT_FIL}")
