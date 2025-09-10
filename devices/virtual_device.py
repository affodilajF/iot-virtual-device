import time
import random
import json
import os
import logging
import paho.mqtt.client as mqtt

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- MQTT Config ---
BROKER = os.getenv("BROKER_HOST", "mqtt-broker")
PORT = int(os.getenv("BROKER_PORT", 1883))
TOPIC = os.getenv("MQTT_TOPIC", "iot/broiler")
DEVICE_ID = os.getenv("DEVICE_ID", "device_01")
INTERVAL = int(os.getenv("INTERVAL", 5))

client = mqtt.Client(DEVICE_ID)

# --- Retry loop to connect broker ---
while True:
    try:
        client.connect(BROKER, PORT, 60)
        logger.info(f"{DEVICE_ID} connected to broker {BROKER}:{PORT}")
        break
    except Exception as e:
        logger.warning(f"{DEVICE_ID} broker not ready, retry in 2s... ({e})")
        time.sleep(2)

# --- Generate random IoT data ---
def generate_data():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(20, 35), 2),
        "humidity": round(random.uniform(50, 90), 2),
        "ammonia": round(random.uniform(0, 50), 2),
        "timestamp": int(time.time())
    }

# --- Main loop ---
while True:
    data = generate_data()
    client.publish(TOPIC, json.dumps(data))
    logger.info(f"{DEVICE_ID} sent: {data}")
    time.sleep(INTERVAL)
