import datetime
from PhoneDisplay.dashboard import status, toggle, log_change, recent_changes, card

def test_toggle_changes_state():
    # Ensure known starting state
    status["light"] = True
    toggle("light", "Light")
    assert status["light"] is False

def test_log_change_adds_entry():
    recent_changes.clear()
    log_change("Light", True)
    assert len(recent_changes) == 1
    entry = recent_changes[0]
    assert "Light turned on" in entry.children[0].children

def test_log_change_keeps_max_5():
    recent_changes.clear()
    for i in range(7):
        log_change("Test", True)
    assert len(recent_changes) == 5

def test_card_renders_correct_state():
    status["gas"] = False
    c = card("Gas", "gas", "💨")
    assert c.id == "gas-card"
    assert "off" in c.className
    assert c.children[1].children == "Off"