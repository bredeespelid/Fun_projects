Dette SwiftUI-skriptet lager en app som lar brukeren bruke mikrofonen på telefonen som inngang og sende utgangen til en ekstern høyttaler via Bluetooth eller AirPlay. Skriptet bruker AVFoundation og AVKit for lydhåndtering og SwiftUI for brukergrensesnittet.

Forutsetninger
For å kjøre dette skriptet trenger du:

Xcode installert på din Mac.
Kunnskap om Swift og SwiftUI.
Funksjonalitet
Skriptet utfører følgende operasjoner:

Opprett AirPlay-knapp: En tilpasset UIViewRepresentable som lager en AirPlay-knapp ved hjelp av AVRoutePickerView.

Lydsesjonshåndtering:

Setter opp en AVAudioEngine for lydbehandling.
Konfigurerer AVAudioSession for å spille og ta opp lyd med Bluetooth-alternativer.
Starter og stopper lydmotoren basert på brukerens handlinger.
Brukergrensesnitt:

Viser et bakgrunnsbilde med justerbar opasitet.
Knapp for å starte og stoppe lydsesjonen.
Knapp for å koble til høyttalere med mikrofon.
AirPlay-knapp for å velge AirPlay-enheter.
Viser bilder i en horisontal rullevisning når brukeren kobler til høyttalere med mikrofon.
