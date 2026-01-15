import json
import time
import serial
import psycopg2
from serial.serialutil import SerialException

# ----------------------------
# Serial (Pico -> Pi)
# ----------------------------
SERIAL_PORT = "/dev/ttyACM0"
BAUD = 115200

# ----------------------------
# Postgres (Pi -> VM via SSH tunnel)
# Make sure your SSH tunnel is running:
#   ssh -L 5432:localhost:5432 wessel@<vm_public_ip>
# ----------------------------
PG_HOST = "127.0.0.1"
PG_PORT = 5432
PG_DB   = "smarthome"
PG_USER = "rpi_bridge"
PG_PASS = "V(eGroen267$"
PG_SSLMODE = "disable"   # tunnel already encrypts traffic

# ----------------------------
# SQL 
# ----------------------------
ACCESS_SQL = """
INSERT INTO public.rfid_checkin (timestamp, tag_id, user_name, access_granted)
VALUES ((%s::timestamp AT TIME ZONE 'UTC'), %s, %s, %s)
"""

LDR_SQL = """
INSERT INTO public.ldr_readings (timestamp, card_id, ldr_raw, ldr_voltage, light_level)
VALUES ((%s::timestamp AT TIME ZONE 'UTC'), %s, %s, %s, %s)
"""

USER_UPSERT_SQL = """
INSERT INTO public.users (tag_id, user_name)
VALUES (%s, %s)
ON CONFLICT (tag_id) DO UPDATE SET user_name = EXCLUDED.user_name
"""

def open_serial():
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
            ser.dtr = False
            ser.rts = False
            time.sleep(0.2)
            ser.reset_input_buffer()
            print("Serial connected:", SERIAL_PORT)
            return ser
        except SerialException as e:
            print("Waiting for Pico...", e)
            time.sleep(1)

def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                dbname=PG_DB,
                user=PG_USER,
                password=PG_PASS,
                sslmode=PG_SSLMODE,
                connect_timeout=10
            )
            conn.autocommit = True
            print("DB connected:", PG_DB, "as", PG_USER)
            return conn
        except Exception as e:
            print("DB connect error:", e)
            time.sleep(5)

def parse_line(line: str):
    """
    Returns: (kind, data_dict) or (None, None)
    kind in {"access", "ldr", "user"}
    """
    if line.startswith("ACCESS_LOG:"):
        payload = line.split("ACCESS_LOG:", 1)[1].strip()
        return "access", json.loads(payload)

    if line.startswith("LDR_LOG:"):
        payload = line.split("LDR_LOG:", 1)[1].strip()
        return "ldr", json.loads(payload)

    if line.startswith("USER_UPDATE:"):
        payload = line.split("USER_UPDATE:", 1)[1].strip()
        return "user", json.loads(payload)

    return None, None

def main():
    ser = open_serial()
    conn = connect_db()
    cur = conn.cursor()

    while True:
        try:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode(errors="replace").strip()
            if not line:
                continue

            kind, data = parse_line(line)
            if not kind:
                continue

            if kind == "access":
                cur.execute(ACCESS_SQL, (
                    data.get("timestamp"),
                    data.get("tag_id"),
                    data.get("user_name"),
                    bool(data.get("access_granted")),
                ))
                print("Inserted ACCESS:", data.get("tag_id"))

            elif kind == "ldr":
                cur.execute(LDR_SQL, (
                    data.get("timestamp"),
                    data.get("card_id"),
                    int(data.get("ldr_raw")),
                    float(data.get("ldr_voltage")),
                    data.get("light_level"),
                ))
                print("Inserted LDR:", data.get("card_id"))

            elif kind == "user":
                try:
                    cur.execute(USER_UPSERT_SQL, (
                        data.get("tag_id"),
                        data.get("user_name"),
                    ))
                    print("Upserted USER:", data.get("tag_id"))
                except Exception as e:
                    print("USER upsert error:", e)
                    print("Tip: add UNIQUE constraint on users.tag_id to enable ON CONFLICT.")

        except SerialException as e:
            print("Serial disconnected:", e)
            try:
                ser.close()
            except:
                pass
            ser = open_serial()

        except Exception as e:
            print("Runtime/Insert error:", e)
            # Reconnect DB on failure
            try:
                cur.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
            conn = connect_db()
            cur = conn.cursor()
            time.sleep(1)

if __name__ == "__main__":
    main()