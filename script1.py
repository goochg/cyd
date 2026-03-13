import requests
import psutil
import time
import urllib.parse
import yaml

# Load secrets from secrets.yaml
try:
    with open('secrets.yaml', 'r') as f:
        secrets = yaml.safe_load(f)
        CYD_IP = secrets['cyd_ip']
except (FileNotFoundError, KeyError):
    print("Error: secrets.yaml not found or 'cyd_ip' key is missing.")
    print("Please create a secrets.yaml file with 'cyd_ip: \"YOUR_IP_HERE\"'")
    exit()

def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return 0.0
        # Common keys for CPU temp on Linux/Windows
        for name in ['coretemp', 'cpu_thermal', 'k10temp', 'zenpower', 'acpitz']:
            if name in temps:
                return temps[name][0].current
        # If no known key, just grab the first one available
        for name, entries in temps.items():
            return entries[0].current
    except Exception:
        return 0.0
    return 0.0

print(f"📡 Pushing stats to ESPHome at {CYD_IP}...")

while True:
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        temp = get_cpu_temp()

        # Encode the entity names for the URL
        cpu_entity = urllib.parse.quote("CPU Usage")
        ram_entity = urllib.parse.quote("RAM Usage")
        temp_entity = urllib.parse.quote("CPU Temp")

        # Push to ESPHome
        requests.post(f"http://{CYD_IP}/number/{cpu_entity}/set?value={cpu}", timeout=1)
        requests.post(f"http://{CYD_IP}/number/{ram_entity}/set?value={ram}", timeout=1)
        requests.post(f"http://{CYD_IP}/number/{temp_entity}/set?value={temp}", timeout=1)

        print(f"🚀 Pushing -> CPU: {cpu}% | RAM: {ram}% | Temp: {temp}C", end="\r")

    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ Error connecting to ESPHome: {e}")
    except Exception as e:
        print(f"\n⚠️ An unexpected error occurred: {e}")

    time.sleep(1)
