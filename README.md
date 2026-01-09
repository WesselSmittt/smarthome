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
