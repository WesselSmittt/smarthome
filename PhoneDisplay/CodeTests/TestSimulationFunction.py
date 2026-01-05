from PhoneDisplay.dashboard import update, status, recent_changes

def test_simulation_updates_state():
    status.update({"light": True, "gas": False, "heating": True, "water": False, "door": False})
    recent_changes.clear()

    # simulate-btn is the last input → only that triggers
    update(None, None, None, None, None, 1)

    assert len(recent_changes) >= 1