import datetime
import json
import ssl
import time

import paho.mqtt.client as mqtt

from awox.config import load_config, AppConfig
from awox.state import DeviceState


# -- Helpers --
def iso_ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
           f"{datetime.datetime.now(datetime.timezone.utc).microsecond // 1000:03d}Z"


class MQTTClient:
    def __init__(self, config: AppConfig, device: DeviceState):
        self.config = config
        self.mqtt_config = config.mqtt
        self.app_config = load_config()
        self.device = device
        self.client = self.configure_client()

    def configure_client(self):
        # AWS IoT on 443 requires ALPN for MQTT
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.device.fingerprint,
            protocol=mqtt.MQTTv311,
        )

        cert_dir = self.app_config.storage.certificate_directory


        ssl_ctx = ssl.create_default_context(cafile= cert_dir / "root-ca.crt")
        ssl_ctx.load_cert_chain(certfile= cert_dir / "device.crt", keyfile= cert_dir / "device.key")
        ssl_ctx.set_alpn_protocols(["x-amzn-mqtt-ca"])
        client.tls_set_context(ssl_ctx)

        client.on_connect = self.on_connect_generator()
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        return client

    def connect(self):
        self.client.connect(self.mqtt_config.endpoint, self.mqtt_config.port, keepalive=60)

        self.client.loop_start()
        time.sleep(2)

    def close(self):

        self.client.loop_stop()
        self.client.disconnect()



    def send_keepalive(self):
        payload = json.dumps({"duration": 180, "publish": 1})
        TOPIC_GR = f"aw/{self.device.account_id}/gr/{self.device.udn}"
        self.client.publish(TOPIC_GR, payload, qos=1)
        print(f"[→] Keepalive → {TOPIC_GR}")



    def make_payload(self, href, method, body):
        return json.dumps({
            "h": href,
            "d": method,
            "m": "application/json",
            "b": body,
            "o": {
                "id": self.device.udn,
                "r": "u",
                "t": iso_ts()
            }
        }, separators=(',', ':'))




    def on_connect_generator(self):

        def on_connect(client, userdata, flags, reason_code, properties):
            # Topics
            print("HERE ")
            print(self.device.device_uuid)
            TOPIC_U = f"aw/{self.device.account_id}/u/{self.device.device_uuid}"
            TOPIC_D = f"aw/{self.device.account_id}/d"
            if reason_code == 0:
                print("[*] Connected to AWS IoT")

                client.subscribe(TOPIC_U, qos=1)
                client.subscribe(TOPIC_D, qos=1)

                print(f"[*] Subscribed to {TOPIC_U} and {TOPIC_D}")
                self.send_keepalive()
            else:
                print(f"[!] Connection failed, code {reason_code}")
        return on_connect

def on_message(client, userdata, msg):
    topic = msg.topic

    try:
        payload = msg.payload.decode("utf-8")
        print(
            f"[←] {topic}: "
            f"{payload[:200]}"
            f"{'...' if len(payload) > 200 else ''}"
        )
    except Exception as e:
        print(f"[←] {topic}: {msg.payload.hex()} (decode err: {e})")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"[!] Disconnected (reason={reason_code})")