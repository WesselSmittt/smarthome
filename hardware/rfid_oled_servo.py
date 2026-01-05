import machine
import time
import json
import ssd1306
from mfrc522 import MFRC522

# === HARDWARE PIN CONFIGURATION ===
# RFID RC522 Connections for Pico

# RFID pins (GPIO numbers)
SCK = 18
MOSI = 19
MISO = 20
RST = 21
CS  = 15

# OLED I2C pins (GPIO 0 and 1)
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# Servo pin (GPIO 16)
servo_pin = machine.Pin(16)
servo_pwm = machine.PWM(servo_pin)
servo_pwm.freq(50)  # 50Hz frequency for servo

# === RFID INITIALIZATION (FIXED) ===
rfid = MFRC522(
    sck=SCK,
    mosi=MOSI,
    miso=MISO,
    rst=RST,
    cs=CS,
    spi_id=0
)

# === OLED INITIALIZATION ===
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# === USER DATA FUNCTIONS ===
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def load_registered_cards():
    try:
        with open('cards.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_registered_cards(cards):
    with open('cards.json', 'w') as f:
        json.dump(cards, f)

# === OLED DISPLAY FUNCTIONS ===
def display_message(lines, clear=True):
    if clear:
        oled.fill(0)

    for i, line in enumerate(lines):
        if i < 8:
            oled.text(line[:20], 0, i * 8)

    oled.show()

def display_welcome():
    display_message([
        "Smart Home",
        "RFID System",
        "Scan Card",
        "to Begin"
    ])

def display_scanning():
    display_message([
        "Scanning...",
        "Please",
        "hold card",
        ""
    ])

def display_access_granted(username):
    display_message([
        "Access Granted",
        "User: " + username,
        "",
        "Welcome!"
    ])

def display_access_denied():
    display_message([
        "Access",
        "Denied",
        "Invalid Card",
        "Try Again"
    ])

def display_register_mode():
    display_message([
        "Register Mode",
        "Scan Card",
        "to Add",
        ""
    ])

def display_deregister_mode():
    display_message([
        "Deregister Mode",
        "Scan Card",
        "to Remove",
        ""
    ])

def display_success():
    display_message([
        "Success!",
        "Operation Complete",
        "",
        ""
    ])

# === SERVO FUNCTIONS (FIXED) ===
def servo_turn_45():
    servo_pwm.duty_u16(2457)  # ~45 degrees
    time.sleep(0.5)

def servo_return_to_center():
    servo_pwm.duty_u16(3276)  # center
    time.sleep(0.5)

# === RFID READING FUNCTION ===
def read_rfid_card():
    (status, _) = rfid.request(rfid.REQIDL)

    if status == rfid.OK:
        (status, uid) = rfid.SelectTagSN()
        if status == rfid.OK:
            card_id = ""
            for b in uid:
                card_id += "%02X" % b
            return card_id

    return None

# === MAIN FUNCTIONS ===
def register_card():
    display_register_mode()
    card_id = read_rfid_card()

    if card_id:
        users = load_users()
        cards = load_registered_cards()

        username = "User" + card_id[-4:]

        users[card_id] = username
        cards.append(card_id)

        save_users(users)
        save_registered_cards(cards)

        display_success()
        time.sleep(2)
        return True

    return False

def deregister_card():
    display_deregister_mode()
    card_id = read_rfid_card()

    if card_id:
        users = load_users()
        cards = load_registered_cards()

        if card_id in users:
            del users[card_id]
        if card_id in cards:
            cards.remove(card_id)

        save_users(users)
        save_registered_cards(cards)

        display_success()
        time.sleep(2)
        return True

    return False

def main():
    print("Smart Home RFID System Started")
    display_welcome()

    while True:
        display_scanning()
        card_id = read_rfid_card()

        if card_id:
            print(f"Card scanned: {card_id}")
            users = load_users()

            if card_id in users:
                username = users[card_id]
                display_access_granted(username)

                servo_turn_45()
                time.sleep(10)
                servo_return_to_center()
            else:
                display_access_denied()
                time.sleep(2)

            time.sleep(1.5)  # debounce
            display_welcome()

        time.sleep(0.1)

# === RUN THE PROGRAM ===
if __name__ == "__main__":
    main()
