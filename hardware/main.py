import machine
import time
import json
import uos
import utime
import ssd1306
from mfrc522 import MFRC522

# === HARDWARE PIN CONFIGURATION ===
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
servo_pwm.freq(50)

# LDR on ADC0 (GPIO26 = physical pin 31)
ldr_adc = machine.ADC(26)

# === RFID INITIALIZATION ===
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

# === FILES ===
USER_FILE = "user_info.json"     # ONLY user file (card_id -> username)
ACCESS_LOG_FILE = "access_log.json"
LDR_LOG_FILE = "ldr_log.json"

# === SERVO CALIBRATION ===
SERVO_HOME = 4915
SERVO_RIGHT_90 = 8192

def servo_go_home():
    servo_pwm.duty_u16(SERVO_HOME)
    time.sleep(0.6)

def servo_turn_90_right():
    servo_pwm.duty_u16(SERVO_RIGHT_90)
    time.sleep(0.8)

# === BASIC JSON HELPERS (reliable write) ===
def _load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def _save_json(filename, obj):
    with open(filename, "w") as f:
        json.dump(obj, f)
        try:
            f.flush()
        except:
            pass
    try:
        uos.sync()
    except:
        pass

# === USERS (ONLY user_info.json) ===
def load_users():
    data = _load_json(USER_FILE, {})
    return data if isinstance(data, dict) else {}

def save_users(users):
    _save_json(USER_FILE, users)

# === LOG HELPERS ===
def now_timestamp():
    t = utime.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

def read_ldr():
    raw = ldr_adc.read_u16()
    voltage = raw * 3.3 / 65535

    if voltage < 0.5:
        level = "Dark"
    elif voltage < 1.5:
        level = "Dim"
    elif voltage < 2.5:
        level = "Normal"
    else:
        level = "Bright"

    return raw, round(voltage, 2), level

def log_ldr_event(ts, card_id):
    raw, voltage, level = read_ldr()
    entry = {
        "timestamp": ts,
        "card_id": card_id,
        "ldr_raw": raw,
        "ldr_voltage": voltage,
        "light_level": level
    }

    logs = _load_json(LDR_LOG_FILE, [])
    if not isinstance(logs, list):
        logs = []
    logs.append(entry)
    _save_json(LDR_LOG_FILE, logs)

    # For Raspberry Pi bridge:
    print("LDR_LOG:", json.dumps(entry))

def log_access_event(ts, card_id, granted, user_name):
    entry = {
        "timestamp": ts,
        "tag_id": card_id,
        "access_granted": granted,
        "user_name": user_name
    }

    logs = _load_json(ACCESS_LOG_FILE, [])
    if not isinstance(logs, list):
        logs = []
    logs.append(entry)
    _save_json(ACCESS_LOG_FILE, logs)

    # For Raspberry Pi bridge:
    print("ACCESS_LOG:", json.dumps(entry))

def emit_user_update(action, card_id, user_name=None):
    msg = {"action": action, "card_id": card_id}
    if user_name is not None:
        msg["user_name"] = user_name
    print("USER_UPDATE:", json.dumps(msg))

# === OLED DISPLAY FUNCTIONS ===
def display_message(lines, clear=True):
    if clear:
        oled.fill(0)
    for i, line in enumerate(lines):
        if i < 8:
            oled.text(line[:20], 0, i * 8)
    oled.show()

def display_welcome():
    display_message(["Smart Home", "RFID System", "Scan Card", "to Begin"])

def display_scanning():
    display_message(["Scanning...", "Please", "hold card", ""])

def display_access_granted(username):
    display_message(["Access Granted", "User: " + username, "", "Welcome!"])

def display_access_denied():
    display_message(["Access", "Denied", "Invalid Card", "Try Again"])

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

def wait_for_card(timeout_ms=1000):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        card_id = read_rfid_card()
        if card_id:
            return card_id
        time.sleep(0.05)
    return None

# === OPTIONAL ADMIN FUNCTIONS (not used automatically) ===
# These are here so you can trigger them later (button/admin mode).
def register_card(card_id, username):
    users = load_users()
    users[card_id] = username
    save_users(users)
    emit_user_update("register", card_id, username)

def deregister_card(card_id):
    users = load_users()
    if card_id in users:
        del users[card_id]
        save_users(users)
    emit_user_update("deregister", card_id)

# === AUTOMATIC SCAN MODE ===
def main():
    print("BOOT: Smart Home RFID System (auto scan)")
    servo_go_home()
    display_welcome()

    while True:
        display_scanning()
        card_id = wait_for_card(1000)

        if card_id:
            ts = now_timestamp()
            print("Card scanned:", card_id)

            # Log light at scan moment
            log_ldr_event(ts, card_id)

            users = load_users()
            if card_id in users:
                username = users[card_id]
                display_access_granted(username)
                log_access_event(ts, card_id, True, username)

                servo_turn_90_right()
                time.sleep(2)
                servo_go_home()
            else:
                display_access_denied()
                log_access_event(ts, card_id, False, "Unknown")
                time.sleep(2)

            time.sleep(1.2)  # debounce
            display_welcome()

        time.sleep(0.1)

# === RUN THE PROGRAM ===
if __name__ == "__main__":
    main()
