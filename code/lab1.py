import adafruit_dht
import board
import time
import paho.mqtt.client as mqtt
import json
import ssl

# --- Dina IoTOpen-uppgifter ---
BROKER = "lynx.iotopen.se"
PORT = 8883
USERNAME = "your-client-id"
PASSWORD = "your-edgenode-password"
CLIENT_ID = "some-unique-client-id"  # Byt ut mot en unik ID

# --- Topics ---
TOPIC_TEMP = "your-client-id/obj/xx/xx" 
TOPIC_HUM  = "your-client-id/obj/tuc/xx"

# --- Initiera sensor ---
sensor = adafruit_dht.DHT11(board.D17)

# --- MQTT Setup ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_ID)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

print(f"Ansluter...")
try:
    client.connect(BROKER, PORT)
    client.loop_start()
    print("✅ Ansluten!")
except Exception as e:
    print(f"Fel: {e}")
    exit()

while True:
    try:
        temp = sensor.temperature
        hum = sensor.humidity
        
        if temp is not None and hum is not None:
            # ÄNDRING: Vi använder "value" istället för "v" för att matcha din LED-logik
            payload_temp = json.dumps({"value": temp})
            payload_hum = json.dumps({"value": hum})
            
            client.publish(TOPIC_TEMP, payload_temp)
            client.publish(TOPIC_HUM, payload_hum)
            
            print(f"Skickat -> Temp: {temp}°C | Fukt: {hum}%")
        else:
            print("Väntar på sensor...")

    except RuntimeError:
        pass 
    
    time.sleep(10)
