def verlichting_check(licht_aan):
    if licht_aan:
        print("Het licht staat nog aan!!")
        antwoord = input("Wilt u dat het licht wordt uitgezet? ").strip().lower()
        if antwoord in ("j", "ja"):
            print("Licht wordt uitgezet.")
            return False
        else:
            print("Licht blijft aan.")
            return True
    else:
        print("Er staan momenteel geen lichten aan.")
        antwoord = input("Wilt u het licht aan zetten? ").strip().lower()
        if antwoord in ("j", "ja"):
            print("Licht wordt nu aangezet.")
            return True
        else:
            print("Geen verandering.")
            return False