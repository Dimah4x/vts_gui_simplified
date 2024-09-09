import paho.mqtt.client as mqtt
import json
from typing import Callable

class MQTTClient:
    def __init__(self, broker: str, port: int, on_message: Callable):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.broker = broker
        self.port = port
        self.user_on_message = on_message

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.client.subscribe("application/+/device/+/event/#")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.user_on_message(msg.topic, payload)
        except json.JSONDecodeError:
            print(f"Failed to decode message: {msg.payload}")

    def publish(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload))