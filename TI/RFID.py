import machine
import utime
import json
import time
from mfrc522 import MFRC522



def init_rfid():

    spi = machine.SPI(0, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
    rfid = MFRC522(spi, machine.Pin(5), machine.Pin(6))
    return rfid



def read_card_id(rfid):
    (stat, tag_type) = rfid.request(rfid.REQIDL)
    if stat == rfid.OK:
        (stat, uid) = rfid.SelectTagSN()
        if stat == rfid.OK:

            card_id = "".join([str(i) for i in uid])
            return card_id
    return None



def get_username(card_id):
    try:
        with open("user_info.json", "r") as f:
            users = json.load(f)
            return users.get(card_id, "Unknown User")
    except Exception as e:
        print(f"Error reading user info: {e}")
        return "Unknown User"



def log_access(card_id, username):

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


    log_entry = {
        "timestamp": timestamp,
        "card_id": card_id,
        "username": username
    }


    try:
        try:
            with open("access_log.json", "r") as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []


        logs.append(log_entry)


        with open("access_log.json", "w") as f:
            json.dump(logs, f, indent=2)

        print(f"Logged access: {username} ({card_id}) at {timestamp}")
        return True
    except Exception as e:
        print(f"Error logging access: {e}")
        return False



def scan_and_log():
    rfid = init_rfid()
    print("RFID Scanner Ready. Scan a card...")

    last_card_id = None

    while True:
        card_id = read_card_id(rfid)

        if card_id and card_id != last_card_id:
            username = get_username(card_id)
            print(f"Card ID: {card_id}")
            print(f"Username: {username}")

            if log_access(card_id, username):
                print("Access logged successfully!")
            else:
                print("Failed to log access")

            last_card_id = card_id
            utime.sleep(2)
        else:
            utime.sleep(0.1)


# Run the scanner
if __name__ == "__main__":
    scan_and_log()
