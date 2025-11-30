def gas_check(gas_aan):
    if gas_aan:
        print("Het gas staat nog open!!")
        antwoord = input("Wilt u dat het gas wordt dichtgedraaid? ").strip().lower()
        if antwoord in ("j", "ja"):
            print("Gas wordt dichtgedraaid.")
            return False
        else:
            print("Gas blijft open.")
            return True
    else:
        print("Het gas staat momenteel dicht.")
        antwoord = input("Wilt u het gas openzetten? ").strip().lower()
        if antwoord in ("j", "ja"):
            print("Gas wordt nu opengedraaid.")
            return True
        else:
            print("Geen verandering.")
            return False