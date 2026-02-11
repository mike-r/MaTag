import ipaddress
import os
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import adafruit_connection_manager
all_haikus = []
feed_name = []
feed_last_value = []

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

print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print(f"Connected to {ssid}!")
print("My IP address is", wifi.radio.ipv4_address)

ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com:", wifi.radio.ping(ipv4), "ms")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("Fetching text from", TIME_URL)
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
speedster_fr_data_from_io = "22"
if io is not None:
    try:
        print("Connect to the Speedster Fuel Remaining IO feed")
        speedster_group = io.get_group("speedster")  # refresh data via HTTP API
        print(speedster_group)
        print()
        print()
        #print("2:", speedster_group[2])
        speedster_feeds = speedster_group["feeds"]
        num_feeds = len(speedster_feeds)
        print("Number of Feeds: ", num_feeds)

        i=0
        for num_feeds in speedster_feeds:
            #print("i: ", i)
            #print({speedster_feeds[i]["name"]}.pop(), {speedster_feeds[i]["last_value"]}.pop())
            feed_name.append({speedster_feeds[i]["name"]}.pop())
            feed_last_value.append({speedster_feeds[i]["last_value"]}.pop())
            print(feed_name[i], feed_last_value[i])
            i=i+1    
        print()

    except:
        print("didnt get AIO feeds")
