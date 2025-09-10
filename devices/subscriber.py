import paho.mqtt.client as mqtt
import logging

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,  # bisa diganti DEBUG untuk lebih detail
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("MQTT-Subscriber")

# --- Callback ketika pesan diterima ---
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logger.info(f"Received on topic '{msg.topic}': {payload}")

# --- MQTT Config ---
BROKER = "localhost"   # atau nama service broker di docker-compose: mqtt-broker
PORT = 1883
TOPIC = "iot/broiler"

client = mqtt.Client("subscriber")
client.on_message = on_message

# --- Connect & subscribe ---
while True:
    try:
        client.connect(BROKER, PORT, 60)
        logger.info(f"Connected to broker {BROKER}:{PORT}")
        break
    except Exception as e:
        logger.warning(f"Broker not ready, retry in 2s... ({e})")
        import time; time.sleep(2)

client.subscribe(TOPIC)
client.loop_forever()
