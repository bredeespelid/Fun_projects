import asyncio
import aiohttp
import pandas as pd
import xml.etree.ElementTree as ET
import json
from aiohttp import ClientSession
from asyncio import Semaphore
import os
import nest_asyncio

# Aktiver nest_asyncio hvis en event loop allerede kjører
try:
    asyncio.get_running_loop()
    nest_asyncio.apply()
except RuntimeError:
    pass

# Input parametere
KOMMUNE_NUMMER = "4601"  # Bergen kommune
NAERINGSKODER = ["93.130"]  # Liste av næringskoder
API_URL = "https://data.brreg.no/enhetsregisteret/api/underenheter"
ENHET_API_URL = "https://data.brreg.no/enhetsregisteret/api/enheter/"
REGNSKAPS_API_URL = "https://data.brreg.no/regnskapsregisteret/regnskap/"
REGNSKAPSTYPE = "SELSKAP"
AAR = 2023
RESULTAT_FIL = r"C:\Users\brede\OneDrive\Skrivebord\Ny mappe\Analyse_trening_Bergen.csv"
CACHE_DRIFTSFIL = 'driftsresultat_cache.json'
CACHE_NAVNFLIL = 'navn_cache.json'
MAX_CONCURRENT_REQUESTS = 10

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
        vedtektsfestet_formaal = data.get('vedtektsfestetFormaal', ['N/A'])
        aktivitet = data.get('aktivitet', ['N/A'])
        navn = data.get('navn', 'N/A')
        return vedtektsfestet_formaal, aktivitet, navn
    else:
        return ["Feil ved henting"], ["Feil ved henting"], "Feil ved henting"

def extract_orgnr_and_driftsresultat(xml_data: str):
    try:
        root = ET.fromstring(xml_data)
        orgnr = root.find('.//virksomhet/organisasjonsnummer').text if root.find('.//virksomhet/organisasjonsnummer') is not None else "N/A"
        driftsresultat = root.find('.//driftsresultat/driftsresultat').text if root.find('.//driftsresultat/driftsresultat') is not None else "N/A"
        return orgnr, driftsresultat
    except ET.ParseError:
        return "N/A", "Ugyldig XML"

async def main():
    # Laste inn cache
    if os.path.exists(CACHE_DRIFTSFIL):
        with open(CACHE_DRIFTSFIL, 'r', encoding='utf-8') as f:
            driftsresultat_cache = json.load(f)
    else:
        driftsresultat_cache = {}

    if os.path.exists(CACHE_NAVNFLIL):
        with open(CACHE_NAVNFLIL, 'r', encoding='utf-8') as f:
            navn_cache = json.load(f)
    else:
        navn_cache = {}

    async with ClientSession() as session:
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

        # Opprett DataFrame med Næringskoder kolonne
        df = pd.DataFrame([{
            'Organisasjonsnummer': unit.get('organisasjonsnummer', ''),
            'Navn': unit.get('navn', ''),
            'Antall Ansatte': unit.get('antallAnsatte', ''),
            'Næringskoder': ', '.join([unit.get('naeringskode1', {}).get('kode', '')]),  # Juster basert på faktisk struktur i API-responsen
            'Kommune': unit.get('beliggenhetsadresse', {}).get('kommune', ''),
            'Adresse': unit.get('beliggenhetsadresse', {}).get('adresse', [''])[0] if unit.get('beliggenhetsadresse', {}).get('adresse') else '',
            'Overordnet Enhet': unit.get('overordnetEnhet', '')
        } for unit in all_units])

        # Identifiser unike Overordnet Enhet orgnr
        unique_orgnr = df['Overordnet Enhet'].dropna().unique()

        # Begrens samtidige forespørsler
        sem = Semaphore(MAX_CONCURRENT_REQUESTS)

        async def process_orgnr(orgnr: str):
            async with sem:
                driftsresultat = "Ingen overordnet enhet"
                vedtektsfestet_formaal, aktivitet, overordnet_navn = ["Ingen overordnet enhet"], ["Ingen overordnet enhet"], "Ingen overordnet enhet"

                if orgnr:
                    # Driftsresultat
                    if orgnr in driftsresultat_cache:
                        driftsresultat = driftsresultat_cache[orgnr]
                    else:
                        xml_data = await get_company_financial_data(session, orgnr, AAR)
                        if not (isinstance(xml_data, str) and (xml_data.startswith("Feil") or xml_data.startswith("Unntak"))):
                            _, drifts = extract_orgnr_and_driftsresultat(xml_data)
                            driftsresultat = drifts if drifts != "N/A" else "Ikke tilgjengelig"
                            driftsresultat_cache[orgnr] = driftsresultat
                        else:
                            driftsresultat = "Feil ved henting"
                            driftsresultat_cache[orgnr] = driftsresultat

                    # Vedtektsfestet Formål og Aktivitet for Overordnet Enhet
                    vedtektsfestet_formaal, aktivitet, overordnet_navn = await get_enhet_details(session, orgnr)

                return orgnr, driftsresultat, vedtektsfestet_formaal, aktivitet, overordnet_navn

        # Opprett oppgaver for å hente detaljer om Overordnet Enhet
        tasks = [process_orgnr(orgnr) for orgnr in unique_orgnr if orgnr]

        # Kjør oppgaver
        print("Starter parallell henting av enhetsdetaljer...")
        results = await asyncio.gather(*tasks)
        print("Fullført henting av enhetsdetaljer.")

        # Lag mapper for rask oppslag
        drifts_map = {orgnr: drifts for orgnr, drifts, _, _, _ in results}
        formaal_map = {orgnr: formaal for orgnr, _, formaal, _, _ in results}
        aktivitet_map = {orgnr: aktivitet for orgnr, _, _, aktivitet, _ in results}
        navn_map = {orgnr: navn for orgnr, _, _, _, navn in results}

        # Map detaljer til DataFrame som nye kolonner
        df['Driftsresultat Overordnet Enhet'] = df['Overordnet Enhet'].map(drifts_map).fillna("Ingen overordnet enhet")
        df['Vedtektsfestet Formål'] = df['Overordnet Enhet'].map(formaal_map).apply(lambda x: ', '.join(x))
        df['Aktivitet'] = df['Overordnet Enhet'].map(aktivitet_map).apply(lambda x: ', '.join(x))
        df['Overordnet Enhet Navn'] = df['Overordnet Enhet'].map(navn_map).fillna("Ingen overordnet enhet")
        
        df.to_csv(RESULTAT_FIL,index=False ,encoding='utf-8-sig')

        print(f"Data lagret til {RESULTAT_FIL}")

# Kjør det asynkrone hovedprogrammet

if __name__ == "__main__":
    asyncio.run(main())
