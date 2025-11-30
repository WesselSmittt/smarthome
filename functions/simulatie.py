import random
import verlichting_check
import gas_check
import verwarming_check
import water_check

class HuisSimulatie:
    def __init__(self):
        # start met random status
        self.licht_aan = random.choice([True, False])
        self.gas_aan = random.choice([True, False])
        self.verwarming_aan = random.choice([True, False])
        self.water_open = random.choice([True, False])

    def status(self):
        print("=== Huidige status van het huis ===")
        print("Licht:", "aan" if self.licht_aan else "uit")
        print("Gas:", "open" if self.gas_aan else "dicht")
        print("Verwarming:", "aan" if self.verwarming_aan else "uit")
        print("Water:", "open" if self.water_open else "dicht")

    def kies_actie(self):
        print("\nWat wilt u controleren?")
        print("1. Licht")
        print("2. Gas")
        print("3. Verwarming")
        print("4. Water")
        keuze = input("Maak een keuze (1-4): ").strip()

        if keuze == "1":
            self.licht_aan = verlichting_check(self.licht_aan)
        elif keuze == "2":
            self.gas_aan = gas_check(self.gas_aan)
        elif keuze == "3":
            self.verwarming_aan = verwarming_check(self.verwarming_aan)
        elif keuze == "4":
            self.water_open = water_check(self.water_open)
        else:
            print("Ongeldige keuze.")

        self.status()

huis = HuisSimulatie()
huis.status()

# gebruiker kan kiezen wat hij wil checken
huis.kies_actie()