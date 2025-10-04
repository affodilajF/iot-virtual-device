import time
import random
import json
import os
import logging
import paho.mqtt.client as mqtt
import signal
import sys

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

status_topic = f"{TOPIC}/status/{DEVICE_ID}"

client = mqtt.Client(DEVICE_ID)

# Setup Last Will and Testament (LWT)
client.will_set(status_topic, payload="offline", qos=1, retain=True)

# Connect to broker
while True:
    try:
        client.connect(BROKER, PORT, 60)
        logger.info(f"{DEVICE_ID} connected to broker {BROKER}:{PORT}")
        break
    except Exception as e:
        logger.warning(f"{DEVICE_ID} broker not ready, retry in 2s... ({e})")
        time.sleep(2)

client.loop_start()

# Publish online status with retain so subscriber knows device is online
payload = {
    "device_id": DEVICE_ID,
    "status": "online"
}
client.publish(status_topic, json.dumps(payload), qos=1, retain=True)
logger.info(f"{DEVICE_ID} status published to {status_topic}: online")

def generate_data():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(20, 35), 2),
        "humidity": round(random.uniform(50, 90), 2),
        "ammonia": round(random.uniform(0, 50), 2),
        "timestamp": int(time.time())
    }

def graceful_exit(signum, frame):
    logger.info("Signal received, publishing offline status and exiting...")
    payload = {
    "device_id": DEVICE_ID,
    "status": "offline"
    }
    client.publish(status_topic, json.dumps(payload), qos=1, retain=True)
    logger.info(f"{DEVICE_ID} status published to {status_topic}: offline")
    time.sleep(1)  # wait to ensure message is sent
    client.loop_stop()
    client.disconnect()
    sys.exit(0)

# Register signal handlers for graceful exit
signal.signal(signal.SIGINT, graceful_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, graceful_exit)  # kill command

# Main loop: publish sensor data
while True:
    data = generate_data()
    topic = f"{TOPIC}/{DEVICE_ID}"
    client.publish(topic, json.dumps(data))
    logger.info(f"{DEVICE_ID} sent to {topic}: {data}")
    time.sleep(INTERVAL)
