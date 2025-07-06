import os, sys, rtc
import wifi, socketpool, ssl
import adafruit_ntp
import adafruit_requests
import displayio

def main():
    return 0


def connect_to_wifi():
    CIRCUITPY_WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
    CIRCUITPY_WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    DEBUG_LOG = int(os.getenv("DEBUG_LOG"))

    try:
        print("Connecting to WiFi...")
        wifi.radio.connect(CIRCUITPY_WIFI_SSID, CIRCUITPY_WIFI_PASSWORD)

        if DEBUG_LOG != 0:
            print("Connected: ", wifi.radio.ipv4_address)
        else:
            print("Connected!")
    except Exception as e:
        print("Failed to Connect to Wifi:", e)


def connect_to_ntp():
    NTP_SERVER = os.getenv("NTP_SERVER")
    TZ_OFFSET = os.getenv("TZ_OFFSET")
    DEBUG_LOG = int(os.getenv("DEBUG_LOG"))

    try:
        # Getting Time from NTP server
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, server=NTP_SERVER, tz_offset=int(TZ_OFFSET))
        current_time = ntp.datetime

        if DEBUG_LOG != 0:
            print("Current Time: ", current_time)
        else:
            print("Time Syned!")

        # Syncing the time to RTC of the CircuitPython device
        rtc.RTC().datetime = current_time

    except Exception as e:
        print("Failed to connect NTP server:", e)


def ensure_wifi_connection():
    if not wifi.radio.connected:
        print("Reconnecting to WiFi...")
        connect_to_wifi()


def create_https_requests():
    try:
        pool = socketpool.SocketPool(wifi.radio)
        https = ssl.create_default_context()
        requests = adafruit_requests.Session(pool, https)
        
    except Exception as e:
        print("Failed to create requests:", e)
    
    return requests


if __name__ == '__main__':
    sys.exit(main())
