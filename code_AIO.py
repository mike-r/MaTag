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

feed_name = []
feed_last_value = []
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
magtag.set_text("batt-Volts: " + str(batt_volts), 2, True)

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

magtag.set_text("IPv4 address: " + str(wifi.radio.ipv4_address), 3, True)

ipv4 = ipaddress.ip_address("8.8.4.4")
#print("Ping google.com:", wifi.radio.ping(ipv4), "ms")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

#rint("Fetching text from", TIME_URL)
response = requests.get(TIME_URL)
print("-" * 40)
print(response.text)
print("-" * 40)

# if there are AIO credentials
if None not in {aio_username, aio_key}:
    print("Initialize connection_manager and requests")
    pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
    ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl_context)
    print("Initialize an Adafruit IO HTTP API object")
    io = IO_HTTP(aio_username, aio_key, requests)

# if the AdafruitIO connection is active
if io is not None:
    try:
        print("Connect to the Speedster and Big Speedey IO feeds")
        speedster_group = io.get_group("speedster")  # refresh data via HTTP API
        big_speedey_group = io.get_group("3pw")
        #print(speedster_group)
        print()
        print()
        speedster_feeds = speedster_group["feeds"]
        big_speedey_feeds = big_speedey_group["feeds"]
        speedster_num_feeds = len(speedster_feeds)
        big_speedey_num_feeds = len(big_speedey_feeds)
        print("Number of Speedster Feeds: ", speedster_num_feeds)
        print("Number of 3PW Feeds: ", big_speedey_num_feeds)




    except:
        print("didnt get AIO feeds")

while True:
    if magtag.peripherals.button_a_pressed:
        print("Button_A Pressed")
        print("Fetching N221TM Data from Adafruit IO")
        magtag.set_text("N221TM",0, False)

        i=0
        for speedster_num_feeds in speedster_feeds:
            feed_name.append({speedster_feeds[i]["name"]}.pop())
            feed_last_value.append({speedster_feeds[i]["last_value"]}.pop())
            if feed_name[i] == "FuelRemaining":
                print(feed_name[i], " ", feed_last_value[i])
                magtag.set_text(feed_name[i] + " " + feed_last_value[i], 1, False)
            elif feed_name[i] == "Hobbs":
                print(feed_name[i], " ", feed_last_value[i])
                magtag.set_text(feed_name[i] + "       " + feed_last_value[i], 2, False)
            elif feed_name[i] == "SmokeLevel":
                print(feed_name[i], " ", feed_last_value[i])
                magtag.set_text(feed_name[i] + "     " + feed_last_value[i], 3, True)
            i=i+1    
        print()

    elif magtag.peripherals.button_b_pressed:
        print("Button_B Pressed")
        print("Fetching N873PW Data from Adafruit IO")
        magtag.set_text("N873PW",0, False)
        i=0
        for big_speedey_num_feeds in big_speedey_feeds:
            big_speedey_feed_name.append({big_speedey_feeds[i]["name"]}.pop())
            big_speedey_feed_last_value.append({big_speedey_feeds[i]["last_value"]}.pop())
            if big_speedey_feed_name[i] == "FuelRemaining":
                print(big_speedey_feed_name[i], " ", big_speedey_feed_last_value[i])
                magtag.set_text(big_speedey_feed_name[i] + " " + big_speedey_feed_last_value[i], 1, False)
            elif big_speedey_feed_name[i] == "Hobbs":
                print(big_speedey_feed_name[i], "  ", big_speedey_feed_last_value[i])
                magtag.set_text(big_speedey_feed_name[i] + "         " + big_speedey_feed_last_value[i], 2, False)
            elif big_speedey_feed_name[i] == "SmokeLevel":
                print(big_speedey_feed_name[i], " ", big_speedey_feed_last_value[i])
                magtag.set_text(big_speedey_feed_name[i] + "     " + big_speedey_feed_last_value[i], 3, True)
            i=i+1    
        print()

    time.sleep(0.5)