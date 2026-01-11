# smarthome
Goedemiddag, wij zijn team Temar. Onze basisapplicatie richt zich op het slim beheren van energie en comfort in huis. 
Denk aan automatische verlichting, temperatuurregeling en energieverbruik inzichtelijk maken. 
Maar wij willen verder gaan dan alleen gemak.


Deze applicatie is een interactieve Smart Home Dashboard gebouwd met Python en Dash. 
Het dashboard combineert real‑time weerinformatie, slimme apparaatstatussen en optionele database‑integratie in één overzichtelijke webinterface.

# Functionaliteiten

## Real‑time Weerkaart (Open‑Meteo API)

- Haalt automatisch het actuele weer op voor Utrecht.
- Toont temperatuur, windsnelheid, luchtvochtigheid en een beschrijving van de weersituatie.
- Vernieuwt elke minuut automatisch.

## Slimme Apparaten (Light, Gas, Heating, Water, Door)

- Elk apparaat heeft een eigen kaart met:
- Huidige status (aan/uit)
- Een knop om de status te toggelen
- Statuswijzigingen worden direct weergegeven in de interface.

## Recent Activity Log

- Houdt de laatste 5 wijzigingen bij.
- Toont:
- Welke actie is uitgevoerd
- Tijdstip van de wijziging
- Een badge met de nieuwe status

## Simulatieknop

- De knop “Simulate Random Change” voert willekeurige statuswijzigingen uit.
- Handig voor testen of demonstraties.

## Optionele PostgreSQL Database‑integratie

- Bij het opstarten probeert de app verbinding te maken met een PostgreSQL‑database.
- Als de database beschikbaar is:
- Wordt een devices‑tabel aangemaakt (indien nodig)
- Worden standaardapparaten toegevoegd
- Worden de actuele statussen uit de database weergegeven
- Als de database offline is:
- Draait de app gewoon door
- Toont het dashboard een melding “Database offline”
- Alle andere functionaliteit blijft werken

## Veilige Configuratie via .env

- Databasegegevens worden niet in de code opgeslagen.
- De app leest host, user, password, etc. uit een .env‑bestand.
- Dit voorkomt dat gevoelige gegevens in Git terechtkomen.

## Sensoren
-De hardware maakt gebruik van meerdere modules om events te meten en acties uit te voeren.

## RFID_Authentication
- RC522 leest de RFID-tag (UID) uit.

- UID wordt vergeleken met geregistreerde gebruikers.

- Resultaat: toegang toegestaan/geweigerd + logregel (ACCESS_LOG).
## Servo motor 
- Servo kan als actuator dienen (bijv. deur/slot simulatie).

- Beweegt naar een ingestelde hoek bij “Access granted” en keert terug naar startpositie.

## LDR sensor
- Meet lichtsterkte via analoge input.

- Logt: raw ADC-waarde, berekende spanning en lichtniveau (bijv. Dark/Dim/Normal/Bright).

- Wordt opgeslagen als LDR_LOG.

## OLED scherm
- Toont systeemstatus (scannen, toegang toegestaan/geweigerd).

- Geeft directe feedback zonder console nodig.

## Data versturen naar database via SSH tunnel
- Pico stuurt logs via USB/serieel naar een Raspberry Pi.

- bridge.py leest de logs, parseert JSON en schrijft naar PostgreSQL.

- SSH-tunnel beveiligt de verbinding zonder de databasepoort publiek open te zetten.

