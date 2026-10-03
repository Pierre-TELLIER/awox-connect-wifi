import datetime
import json
import ssl
from logging import debug, info, error

import paho.mqtt.client as mqtt

from awox.config import AppConfig
from awox.state import DeviceState


# -- Helpers --
def iso_ts():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


class MQTTClient:
    def __init__(self, config: AppConfig, device: DeviceState):
        self.config = config
        self.mqtt_config = config.mqtt
        self.device = device
        self.client = self.configure_client()

    def configure_client(self):
        # AWS IoT on 443 requires ALPN for MQTT
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.device.fingerprint,
            protocol=mqtt.MQTTv311,
        )

        cert_dir = self.config.storage.certificate_directory

        ssl_ctx = ssl.create_default_context(cafile=cert_dir / "root-ca.crt")
        ssl_ctx.load_cert_chain(certfile=cert_dir / "device.crt", keyfile=cert_dir / "device.key")
        ssl_ctx.set_alpn_protocols(["x-amzn-mqtt-ca"])
        client.tls_set_context(ssl_ctx)

        client.on_connect = self.on_connect_generator()
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        return client

    def connect(self):
        self.client.connect(self.mqtt_config.endpoint, self.mqtt_config.port, keepalive=60)
        self.client.loop_start()

    def close(self):

        self.client.loop_stop()
        self.client.disconnect()

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
            debug(self.device.device_uuid)
            TOPIC_U = f"aw/{self.device.account_id}/u/{self.device.device_uuid}"
            TOPIC_D = f"aw/{self.device.account_id}/d"
            if reason_code == 0:
                info("[*] Connected to AWS IoT")

                client.subscribe(TOPIC_U, qos=1)
                client.subscribe(TOPIC_D, qos=1)
                debug(f"[*] Subscribed to {TOPIC_U} and {TOPIC_D}")
            else:
                info(f"[!] Connection failed, code {reason_code}")

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
        error(f"[←] {topic}: {msg.payload.hex()} (decode err: {e})")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    info(f"[!] Disconnected (reason={reason_code})")
