import ipaddress
import os
import time
import terminalio
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import adafruit_connection_manager
from adafruit_magtag.magtag import MagTag

feed_name = None
feed_last_value = None
big_speedey_feed_name = []
big_speedey_feed_last_value = []

# Get our username, key and desired timezone
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = os.getenv("ADAFRUIT_AIO_USERNAME")
aio_key = os.getenv("ADAFRUIT_AIO_KEY")
timezone = os.getenv("TIMEZONE")
TIME_URL = f"https://io.adafruit.com/api/v2/{aio_username}/integrations/time/strftime?x-aio-key={aio_key}&tz={timezone}"
TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"

print("ESP32-S2 Adafruit IO Time test")

print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#print("Available WiFi networks:")
#for network in wifi.radio.start_scanning_networks():
    #print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            #network.rssi, network.channel))
#wifi.radio.stop_scanning_networks()

print("Connecting to", ssid)

wifi_good = False

# if there are AIO credentials
if None not in {aio_username, aio_key}:
    print("Initialize connection_manager and requests")
    pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
    ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl_context)
    print("Initialize an Adafruit IO HTTP API object")
    io = IO_HTTP(aio_username, aio_key, requests)

def pull_feeds(aircraft):
    try:
        print("Connect to the Speedster and Big Speedey IO feeds")
        aircraft_group = io.get_group(aircraft)  # refresh data via HTTP API
        print(aircraft_group)
        print()
        print()
        feeds = aircraft_group["feeds"]
        print("feeds type: ", type(feeds))
        print("feeds: ", feeds)
        print()
        return feeds
    except:
        print("didnt get AIO feeds")

def print_feeds(aircraft, registration):
        print("Button for ", registration, " Pressed")
        print("Fetching", registration, " Data from Adafruit IO")
        feeds = pull_feeds(aircraft)
        magtag.set_text(registration,0, False)
        for i in range(len(feeds)):
            feed_name = feeds[i]["name"]
            feed_last_value = feeds[i]["last_value"]
            if feed_name == "FuelRemaining":
                print(feed_name, " ", feed_last_value)
                magtag.set_text(feed_name + " " + feed_last_value, 1, False)
            elif feed_name == "Hobbs":
                print(feed_name, " ", feed_last_value)
                magtag.set_text(feed_name + "       " + feed_last_value, 2, False)
            elif feed_name == "SmokeLevel":
                print(feed_name, " ", feed_last_value)
                magtag.set_text(feed_name + "     " + feed_last_value, 3, True) 
        print()
        print("feed_name: ", feed_name)
        print("feed_last_value: ", feed_last_value)
        print()

magtag = MagTag()
magtag.peripherals.neopixel_disable = False
batt_volts = magtag.peripherals.battery
print("Battery Voltage: ", batt_volts)

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(145, 17),
    text_scale=4,
    text_anchor_point=(0.5, 0.5),
)

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(10, 55),
    text_scale=2,
    #text_anchor_point=(0.5, 0.5),
)

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(10, 80),
    text_scale=2,
    #text_anchor_point=(0.5, 0.5),
)

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(10, 105),
    text_scale=2,
    #text_anchor_point=(0.5, 0.5),
)

magtag.set_text("TronView",0, False)
magtag.set_text("Batt-Volts: " + str(batt_volts), 1, False)

while not wifi_good:
    try:
        wifi.radio.connect(ssid, password)
        wifi_good = True
    except:
        print("Hangar SSID not avaliable")
        time.sleep(10)
        wifi_good - False

print(f"Connected to {ssid}!")
print("My IP address is", wifi.radio.ipv4_address)

magtag.set_text("WiFi:" + str(wifi.radio.ipv4_address), 3, True)

ipv4 = ipaddress.ip_address("8.8.4.4")
#print("Ping google.com:", wifi.radio.ping(ipv4), "ms")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

#rint("Fetching text from", TIME_URL)
response = requests.get(TIME_URL)
print("-" * 40)
print(response.text)
print("-" * 40)

while True:
    if magtag.peripherals.button_a_pressed:
        print("Button_A Pressed")
        aircraft = "speedster"
        registration = "N221TM"
        print("Fetching ", registration, " aka ", aircraft, " Data from Adafruit IO")
        print_feeds(aircraft, registration)
    elif magtag.peripherals.button_b_pressed:
        print("Button_B Pressed")
        aircraft = "big-speedey"
        registration = "N873PW"
        print("Fetching ", registration, " aka ", aircraft, " Data from Adafruit IO")
        print_feeds(aircraft, registration)
    elif magtag.peripherals.button_c_pressed:
        print("Button_C Pressed Do nothing")
    elif magtag.peripherals.button_d_pressed:
        print("Button_D Pressed Do nothing")

    time.sleep(0.25)