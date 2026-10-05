from awox.mqtt.client import MQTTClient
from awox.state import Device


class Light:
    def __init__(
            self,
            mqtt: MQTTClient,
            device_id: str,
            device: Device,
    ):
        self.mqtt = mqtt
        self.device_id = device_id
        self.device_config = device.config

    @property
    def command_topic(self) -> str:
        return (
            f"aw/{self.device_config.account_id}"
            f"/r/{self.device_config.bridge_gateware_id}"
            f"/{self.device_config.udn}"
        )

    def send_command(self, payload) -> None:
        self.mqtt.publish(
            self.command_topic,
            payload,
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

        self.send_command(payload)

    def set_brightness(self, level: int) -> None:
        if not 0 <= level <= 100:
            raise ValueError("Brightness must be between 0 and 100")

        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/lightdimming",
            "PUT",
            {"dimmingSetting": level},
        )

        self.send_command(payload)

    def set_color(self, r: int, g: int, b: int) -> None:
        for value in (r, g, b):
            if not 0 <= value <= 255:
                raise ValueError("RGB values must be between 0 and 255")

        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/colorrgb",
            "PUT",
            {"rgbValue": [r, g, b]},
        )

        self.send_command(payload)

    def set_temperature(self, temperature: int) -> None:
        if not 0 <= temperature <= 100:
            raise ValueError("Temperature must be between 0 and 100")

        payload = self.mqtt.make_payload(
            f"/v1/devices/{self.device_id}/lighttemperature",
            "PUT",
            {"temperatureSetting": temperature},
        )

        self.send_command(payload)
