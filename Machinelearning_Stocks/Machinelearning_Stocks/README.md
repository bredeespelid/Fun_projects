Dette skriptet laster ned historiske aksjepriser, utfører maskinlæringsprognoser ved hjelp av en Random Forest-modell, og lagrer resultatene i en tabell. Skriptet er tilpasset bruk med Python og bibliotekene pandas, yfinance, og sklearn.

Forutsetninger
For å kjøre dette skriptet trenger du Python 3.x installert på systemet ditt sammen med følgende Python-pakker: pandas, yfinance, og sklearn.

Funksjonalitet
Skriptet utfører følgende operasjoner:

Last ned historiske data: Skriptet bruker yfinance til å laste ned historiske data for en liste med aksjer.

Forbered data:

Fjerner kolonner for utbytte og aksjesplitt.
Legger til en kolonne for morgendagens lukkekurs.
Lager en målkolonne som indikerer om morgendagens lukkekurs er høyere enn dagens.
Lag tilleggsvariabler:

Beregner rullerende gjennomsnitt for flere horisonter.
Lager kolonner for forholdet mellom dagens lukkekurs og det rullerende gjennomsnittet.
Lager kolonner for summen av positive trender over flere horisonter.
Bygg og tren modell: Bruker RandomForestClassifier fra sklearn til å bygge en modell basert på de tilleggsvariablene.

Tilbakeprøving:

Deler dataene i trenings- og testsett.
Trener modellen på treningssettet og predikerer på testsettet.
Kombinerer prediksjonene med de faktiske verdiene for evaluering.
Evaluering: Skriptet beregner presisjon for hver aksje og lagrer resultatene i en tabell.

Lagre resultatene: Resultatene lagres i en tabell med kolonnene 'Date', 'Predictions', 'Precision', og 'Ticker'.

Bruk
Kjør Skriptet: Kjør skriptet i et Python-miljø.
Skriptet laster ned data og utfører maskinlæringsprognoser: Skriptet laster automatisk ned data for de spesifiserte aksjene, trener modellen, og utfører prediksjoner.
Se Resultatene: Resultatene vises som en tabell i konsollen.
