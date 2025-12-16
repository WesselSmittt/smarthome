import random

def verlichting_check(status):
    print("Controle van verlichting...")
    nieuw_status = not status  # toggle status
    if not nieuw_status:
        print("Het licht is nu uit.")
    else:
        print("Het licht is nu aan.")
    return nieuw_status

def gas_check(status):
    print("Controle van gas...")
    nieuw_status = not status
    if not nieuw_status:
        print("Het gas is nu dicht.")
    else:
        print("Het gas is nu open.")
    return nieuw_status

def verwarming_check(status):
    print("Controle van verwarming...")
    nieuw_status = not status
    if not nieuw_status:
        print("De verwarming is nu uit.")
    else:
        print("De verwarming is nu aan.")
    return nieuw_status

def water_check(status):
    print("Controle van water...")
    nieuw_status = not status
    if not nieuw_status:
        print("Het water is nu dicht.")
    else:
        print("Het water is nu open.")
    return nieuw_status

class HuisSimulatie:
    def __init__(self):
        # start met random status
        self.licht_aan = random.choice([True, False])
        self.gas_aan = random.choice([True, False])
        self.verwarming_aan = random.choice([True, False])
        self.water_open = random.choice([True, False])

    def status(self):
        print("\n=== Huidige status van het huis ===")
        print("Licht:", "aan" if self.licht_aan else "uit")
        print("Gas:", "open" if self.gas_aan else "dicht")
        print("Verwarming:", "aan" if self.verwarming_aan else "uit")
        print("Water:", "open" if self.water_open else "dicht")

    def alles_uit(self):
        self.licht_aan = False
        self.gas_aan = False
        self.verwarming_aan = False
        self.water_open = False
        print("\nAlle functies zijn uitgezet!")
        print("Het licht is nu uit.")
        print("Het gas is nu dicht.")
        print("De verwarming is nu uit.")
        print("Het water is nu dicht.")

    def kies_actie(self):
        print("\nWat wilt u controleren?")
        print("1. Licht")
        print("2. Gas")
        print("3. Verwarming")
        print("4. Water")
        print("5. Alles uitzetten")
        print("Typ 'stop' om te stoppen.")
        keuze = input("Maak een keuze (1-5 of 'stop'): ").strip().lower()

        if keuze == "1":
            self.licht_aan = verlichting_check(self.licht_aan)
        elif keuze == "2":
            self.gas_aan = gas_check(self.gas_aan)
        elif keuze == "3":
            self.verwarming_aan = verwarming_check(self.verwarming_aan)
        elif keuze == "4":
            self.water_open = water_check(self.water_open)
        elif keuze == "5":
            self.alles_uit()
        elif keuze == "stop":
            return False  # beëindig loop
        else:
            print("Ongeldige keuze.")

        self.status()
        return True  # blijf doorgaan

# hoofdprogramma
huis = HuisSimulatie()
huis.status()

while True:
    doorgaan = huis.kies_actie()
    if not doorgaan:
        print("\nProgramma gestopt. Tot ziens!")
        break