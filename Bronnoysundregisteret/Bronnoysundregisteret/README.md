# BAN443_termpaper
## Markedsanalyse

Structured output at scale:
<- classification
<- named entity recognition
<- generation with/without external information

Evaluate the quality of output: 
<- Human inspection for random sub-sample
<- Hard-coded rules (missing data, etc).
<- Using an LLM for evaluation. 

Dette prosjektet bruker ulike API-er for å samle inn bedrifts- og finansdata som grunnlag for markedsanalyser. Datakildene inkluderer:

## Data Sources
- **SSB API**: Fetches industry codes (NACE codes). {Input: finn koder/ navn som matcher kaffebransjen}
- **Brønnøysundregisteret API**: Provides company names and addresses. {Input: By. Eksisterende funn: næringskode -> Finner orgnummer}
- **Brønnøysund Regnskapsregister API**: Retrieves financial data such as operating results.{Eksisterende funn: Finn finansiell informasjon basert på orgnummer }
- https://data.brreg.no/regnskapsregisteret/regnskap/swagger-ui/swagger-ui/index.html#/

## Example Usage
### Input
"Lag en markedsanalyse for kaffebransjen i Bergen."

### Output
- The largest companies are: {...}
- Companies with the highest revenue: {...}

## Chat API

ChatGPT API for å integrere et AI-basert verktøy i ditt prosjekt som kan analysere og oppsummere data hentet fra ulike API-er, som SSB, Brønnøysundregisteret og Regnskapsregisteret. Dette kan gjøres slik:

Data Collection: Først samler du inn data fra de eksterne API-ene (SSB, Brønnøysund, Regnskapsregisteret) ved å bruke vanlige HTTP-forespørsler i Python.

Analyse og oppsummering: Bruk ChatGPT API til å generere oppsummeringer, analyser eller innsikter fra de innsamlede dataene. Eksempel:

Generere en oppsummering av regnskapet til et selskap.
Identifisere trender i markedsdata basert på næringskoder og inntektsinformasjon.
Automatisert innsikt: Du kan lage en automatisert prosess som sender dataene til ChatGPT API for analyse og genererer en detaljert rapport eller konklusjon, som for eksempel hvilke selskaper som har høyest omsetning eller hvordan det økonomiske bildet ser ut for en bransje.


## API Structures

### Struktur_næringskode:
```json
{
    "code": "01",
    "parentCode": "A",
    "level": "2",
    "name": "Jordbruk og tjenester tilknyttet jordbruk, jakt og viltstell",
    "shortName": "Jordbruk, tilhør. tjenester, jakt",
    "presentationName": "",
    "validFrom": null,
    "validTo": null,
    "notes": "Inkluderer: Denne næringen omfatter to basisaktiviteter: produksjon av vegetabilske og animalske produkter, jordbruk, dyrking av genetisk modifiserte vekster og oppdrett av genetisk modifiserte dyr..."
}

```


### Struktur_brreg:
```json
{
  "organisasjonsnummer": "932740265",
  "navn": "AJ SCHOUTEN AS",
  "organisasjonsform": {
    "kode": "AS",
    "beskrivelse": "Aksjeselskap",
    "_links": {
      "self": {
        "href": "https://data.brreg.no/enhetsregisteret/api/organisasjonsformer/AS"
      }
    }
  },
  "postadresse": {
    "land": "Norge",
    "landkode": "NO",
    "postnummer": "0365",
    "poststed": "OSLO",
    "adresse": [
      "c/o Alexandra Jansen Schouten",
      "Fauchalds gate 9B"
    ],
    "kommune": "OSLO",
    "kommunenummer": "0301"
  },
  "registreringsdatoEnhetsregisteret": "2024-01-02",
  "registrertIMvaregisteret": true,
  "naeringskode1": {
    "kode": "47.241",
    "beskrivelse": "Butikkhandel med bakervarer og konditorvarer"
  },
  "antallAnsatte": 10,
  "harRegistrertAntallAnsatte": true,
  "forretningsadresse": {
    "land": "Norge",
    "landkode": "NO",
    "postnummer": "0352",
    "poststed": "OSLO",
    "adresse": [
      "Oscars gate 19"
    ],
    "kommune": "OSLO",
    "kommunenummer": "0301"
  },
  "stiftelsesdato": "2023-10-26",
  "institusjonellSektorkode": {
    "kode": "2100",
    "beskrivelse": "Private aksjeselskaper mv."
  },
  "registrertIForetaksregisteret": true,
  "registrertIStiftelsesregisteret": false,
  "registrertIFrivillighetsregisteret": false,
  "konkurs": false,
  "underAvvikling": false,
  "underTvangsavviklingEllerTvangsopplosning": false,
  "maalform": "Bokmål",
  "vedtektsdato": "2023-10-26",
  "vedtektsfestetFormaal": [
    "Drift av bakeriutsalg og det som naturlig hører sammen med dette."
  ],
  "aktivitet": [
    "Butikkhandel med bakervarer."
  ],
  "_links": {
    "self": {
      "href": "https://data.brreg.no/enhetsregisteret/api/enheter/932740265"
    }
  }
}

```


### Struktur_brreg_regnskapsregister:

```xml
<ArrayList>
  <item>
    <id>5415737</id>
    <journalnr>2024741804</journalnr>
    <regnskapstype>SELSKAP</regnskapstype>
    <virksomhet>
      <organisasjonsnummer>874383562</organisasjonsnummer>
      <organisasjonsform>AS</organisasjonsform>
      <morselskap>false</morselskap>
    </virksomhet>
    <regnskapsperiode>
      <fraDato>2023-01-01</fraDato>
      <tilDato>2023-12-31</tilDato>
    </regnskapsperiode>
    <valuta>NOK</valuta>
    <avviklingsregnskap>false</avviklingsregnskap>
    <oppstillingsplan>store</oppstillingsplan>
    <revisjon>
      <ikkeRevidertAarsregnskap>false</ikkeRevidertAarsregnskap>
      <fravalgRevisjon>false</fravalgRevisjon>
    </revisjon>
    <regnkapsprinsipper>
      <smaaForetak>true</smaaForetak>
      <regnskapsregler>regnskapslovenAlminneligRegler</regnskapsregler>
    </regnkapsprinsipper>
    <egenkapitalGjeld>
      <sumEgenkapitalGjeld>7471397.00</sumEgenkapitalGjeld>
      <egenkapital>
        <sumEgenkapital>3620340.00</sumEgenkapital>
        <opptjentEgenkapital>
          <sumOpptjentEgenkapital>3338369.00</sumOpptjentEgenkapital>
        </opptjentEgenkapital>
        <innskuttEgenkapital>
          <sumInnskuttEgenkapital>281971.00</sumInnskuttEgenkaptial>
        </innskuttEgenkapital>
      </egenkapital>
      <gjeldOversikt>
        <sumGjeld>3851057.00</sumGjeld>
        <kortsiktigGjeld>
          <sumKortsiktigGjeld>3015890.00</sumKortsiktigGjeld>
        </kortsiktigGjeld>
        <langsiktigGjeld>
          <sumLangsiktigGjeld>835167.00</sumLangsiktigGjeld>
        </langsiktigGjeld>
      </gjeldOversikt>
    </egenkapitalGjeld>
    <eiendeler>
      <sumEiendeler>7471397.00</sumEiendeler>
      <omloepsmidler>
        <sumOmloepsmidler>1326383.00</sumOmloepsmidler>
      </omloepsmidler>
      <anleggsmidler>
        <sumAnleggsmidler>6145015.00</sumAnleggsmidler>
      </anleggsmidler>
    </eiendeler>
    <resultatregnskapResultat>
      <ordinaertResultatFoerSkattekostnad>2295479.00</ordinaertResultatFoerSkattekostnad>
      <aarsresultat>1789315.00</aarsresultat>
      <totalresultat>1789315.00</totalresultat>
      <finansresultat>
        <nettoFinans>87291.00</nettoFinans>
        <finansinntekt>
          <sumFinansinntekter>179800.00</sumFinansinntekter>
        </finansinntekt>
        <finanskostnad>
          <sumFinanskostnad>92509.00</sumFinanskostnad>
        </finanskostnad>
      </finansresultat>
      <driftsresultat>
        <driftsresultat>2208188.00</driftsresultat>
        <driftsinntekter>
          <sumDriftsinntekter>28725566.00</sumDriftsinntekter>
        </driftsinntekter>
        <driftskostnad>
          <sumDriftskostnad>26517378.00</sumDriftskostnad>
        </driftskostnad>
      </driftsresultat>
    </resultatregnskapResultat>
  </item>
</ArrayList>

```


