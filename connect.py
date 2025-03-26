import network
import json


def get_creds():
    with open("/.creds", "r") as f:
        creds = json.load(f)
        return creds


def connect_to_wlan():
    creds = get_creds()
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(creds["ssid"], creds["password"])
    print(f"Connected: {station.isconnected()}")
    
    
def print_kwargs(**kwargs):
    for k, v in kwargs.items():
        print(f"key {k}: {v}")
