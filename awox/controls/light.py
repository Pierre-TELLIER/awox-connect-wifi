from awox.mqtt.client import MQTTClient
from awox.state import DeviceState


class Light:
    def __init__(
        self,
        mqtt: MQTTClient,
        device_id: str,
        device: DeviceState,
    ):
        self.mqtt = mqtt
        self.device_id = device_id
        self.device = device

    @property
    def command_topic(self) -> str:
        return (
            f"aw/{self.device.account_id}"
            f"/r/{self.device.bridge_gateware_id}"
            f"/{self.device.udn}"
        )

    def turn_on(self) -> None:
        self._send_power(True)

    def turn_off(self) -> None:
        self._send_power(False)

    def _send_power(self, state: bool) -> None:
        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/switch",
            "PUT",
            {"value": 1 if state else 0},
        )

        self.mqtt.client.publish(
            self.command_topic,
            payload,
            qos=1,
        )

        print(
            f"[→] Power {'ON' if state else 'OFF'} "
            f"→ {self.command_topic}"
        )

    def set_brightness(self, level: int) -> None:
        if not 0 <= level <= 100:
            raise ValueError("Brightness must be between 0 and 100")

        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/lightdimming",
            "PUT",
            {"dimmingSetting": level},
        )

        self.mqtt.client.publish(
            self.command_topic,
            payload,
            qos=1,
        )

        print(
            f"[→] Brightness {level} "
            f"→ {self.command_topic}"
        )

    def set_color(self, r: int, g: int, b: int) -> None:
        for value in (r, g, b):
            if not 0 <= value <= 255:
                raise ValueError("RGB values must be between 0 and 255")

        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/colorrgb",
            "PUT",
            {"rgbValue": [r, g, b]},
        )

        self.mqtt.client.publish(
            self.command_topic,
            payload,
            qos=1,
        )

        print(
            f"[→] Color RGB({r},{g},{b}) "
            f"→ {self.command_topic}"
        )


    def set_temperature(self, temperature: int) -> None:
        if not 0 <= temperature <= 100:
            raise ValueError("Temperature must be between 0 and 100")

        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/lighttemperature",
            "PUT",
            {"temperatureSetting": temperature},
        )

        self.mqtt.client.publish(
            self.command_topic,
            payload,
            qos=1,
        )

        print(
            f"[→] Temperature {temperature} "
            f"→ {self.command_topic}"
        )
