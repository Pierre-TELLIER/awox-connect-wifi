import datetime
import json
import ssl
import threading
from logging import debug, info, error

import paho.mqtt.client as mqtt

from awox.config import AppConfig
from awox.state import DeviceState, Device, save_device_state


def parse_light_state(payload, state: DeviceState):
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    data = json.loads(payload)

    for resource in data.get("links", []):
        href = resource.get("href")

        if href == "switch":
            state.power = bool(resource.get("value"))

        elif href == "lightmode":
            state.mode = resource.get("lightMode")

        elif href == "lightdimming":
            state.brightness = int(resource.get("dimmingSetting"))

        elif href == "lighttemperature":
            state.temperature = int(resource.get("temperatureSetting"))

        elif href == "colorrgb":
            state.rgb = resource.get("rgbValue")

        state.connected = True

    return state


# -- Helpers --
def iso_ts():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


class MQTTClient:
    def __init__(self, config: AppConfig, device: Device):
        self.config = config
        self.mqtt_config = config.mqtt
        self.device_config = device.config
        self.device_state = device.state
        self._client = self.configure_client()

        self.connected_event = threading.Event()
        self._pending = []

    def configure_client(self):
        # AWS IoT on 443 requires ALPN for MQTT
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.device_config.fingerprint,
            protocol=mqtt.MQTTv311,
        )

        cert_dir = self.config.storage.certificate_directory

        ssl_ctx = ssl.create_default_context(cafile=cert_dir / "root-ca.crt")
        ssl_ctx.load_cert_chain(certfile=cert_dir / "device.crt", keyfile=cert_dir / "device.key")
        ssl_ctx.set_alpn_protocols(["x-amzn-mqtt-ca"])
        client.tls_set_context(ssl_ctx)

        client.on_connect = self.on_connect_generator()
        client.on_message = self.on_message_generator()
        client.on_disconnect = self.on_disconnect_generator()
        return client

    def connect(self):
        self._client.connect(self.mqtt_config.endpoint, self.mqtt_config.port, keepalive=60)
        self._client.loop_start()

    def close(self):
        self.flush()
        self._client.disconnect()
        self._client.loop_stop()

    def publish(self, topic, payload):
        msg_info = self._client.publish(topic, payload, qos=1)
        self._pending.append(msg_info)
        return msg_info

    def flush(self, timeout=5):
        """Block (main thread only) until queued messages are acknowledged."""
        for msg_info in self._pending:
            msg_info.wait_for_publish(timeout=timeout)
        self._pending.clear()

    def send_keepalive(self):
        payload = json.dumps({"duration": 180, "publish": 1})
        TOPIC_GR = f"aw/{self.device_config.account_id}/gr/{self.device_config.udn}"
        self.publish(TOPIC_GR, payload)
        debug(f"[→] Keepalive → {TOPIC_GR}")

    def make_payload(self, href, method, body):
        return json.dumps({
            "h": href,
            "d": method,
            "m": "application/json",
            "b": body,
            "o": {
                "id": self.device_config.udn,
                "r": "u",
                "t": iso_ts()
            }
        }, separators=(',', ':'))

    def on_connect_generator(self):

        def on_connect(client, userdata, flags, reason_code, properties):
            # Topics
            debug(self.device_config.device_uuid)
            TOPIC_U = f"aw/{self.device_config.account_id}/u/{self.device_config.bridge_gateware_id}"
            TOPIC_D = f"aw/{self.device_config.account_id}/d"
            # Topic used to get the response of the command.
            # May be useful if we want to keep a success/failure.
            TOPIC_R = f"aw/{self.device_config.account_id}/r/{self.device_config.bridge_gateware_id}/#"
            ALL_TOPIC_DEBUG = f"aw/{self.device_config.account_id}/#"

            if reason_code == 0:
                info("[*] Connected to AWS IoT")

                client.subscribe(TOPIC_U, qos=1)
                client.subscribe(TOPIC_D, qos=1)
                # client.subscribe(ALL_TOPIC_DEBUG, qos=1)

                debug(f"[*] Subscribed to {TOPIC_U},{TOPIC_D}")
                self.send_keepalive()  # The keepalive is used to get the state of the device. It isn't useful to keep the connection alive
                self.connected_event.set()
            else:
                info(f"[!] Connection failed, code {reason_code}")

        return on_connect

    def on_message_generator(self):

        def on_message(client, userdata, msg):
            topic = msg.topic
            try:
                payload = msg.payload.decode("utf-8")
                # If the message is on the return info topic i.e. gives information on the light status
                if topic == f'aw/{self.device_config.account_id}/u/{self.device_config.bridge_gateware_id}':
                    parse_light_state(payload, self.device_state)
                else:
                    debug(
                        f"[←] {topic}: "
                        f"{payload[:200]}"
                        f"{'...' if len(payload) > 200 else ''}"
                    )
            except Exception as e:
                error(f"[←] {topic}: {msg.payload.hex()} (decode err: {e})")

        return on_message

    def on_disconnect_generator(self):
        def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
            info(f"[!] Disconnected (reason={reason_code})")
            self.device_state.connected = False
            save_device_state(self.config.storage.state_file, self.device_config.device_id, self.device_state)

        return on_disconnect

    def wait_for_readiness(self, timeout=15):
        if not self.connected_event.wait(timeout):
            raise TimeoutError("Could not connect to AWS IoT")
