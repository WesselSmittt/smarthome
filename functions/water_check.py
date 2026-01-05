def water_check(water_open):
    if water_open:
        print("Er staat nog een kraan open!!")
        antwoord = input("Wilt u dat de kraan wordt dichtgedraaid? ").strip().lower()
        if antwoord in ("j", "ja"):
            print("Kraan wordt dichtgedraaid.")
            return False
        else:
            print("Kraan blijft open.")
            return True
    else:
        print("Alle kranen staan momenteel dicht.")
        antwoord = input("Wilt u een kraan openzetten? ").strip().lower()
        if antwoord in ("j", "ja"):
            print("Kraan wordt nu opengedraaid.")
            return True
        else:
            print("Geen verandering.")
            return False