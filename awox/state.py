import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CURRENT_VERSION = 1


@dataclass
class CertificateState:
    device_cert: Path
    device_key: Path
    ca_cert: Path
    root_ca: Path


@dataclass
class DeviceConfig:
    friendly_name: str | None = None
    account_id: str | None = None
    bridge_gateware_id: str | None = None
    device_id: str | None = None
    device_uuid: str | None = None
    udn: str | None = None
    fingerprint: str | None = None
    mqtt_endpoint: str | None = None


@dataclass
class DeviceState:
    power: bool | None = None
    mode: str | None = None
    brightness: int | None = None
    temperature: int | None = None
    rgb: tuple[int, int, int] | None = None
    connected: bool = False


@dataclass
class Device:
    config: DeviceConfig | None = None
    state: DeviceState | None = None


@dataclass
class AppState:
    version: int = CURRENT_VERSION
    certificates: CertificateState | None = None
    devices: dict[str, Device] = field(default_factory=dict)
    provisioned: bool = False


def load_state(path: Path) -> AppState:
    """
    Load application state from a YAML file.

    If the file doesn't exist, return an empty, unprovisioned state.
    """
    if not path.exists():
        return AppState()

    with path.open("r") as f:
        data = yaml.safe_load(f) or {}

    if not data:
        return AppState()
    version = data.get("version", 1)  # files from before versioning are v1
    if version > CURRENT_VERSION:
        raise RuntimeError(
            f"{path} was written by a newer awox (state version {version}, "
            f"this one supports {CURRENT_VERSION}). Upgrade awox."
        )

    certificates_data = data.get("certificates")

    certificates = None
    if certificates_data:
        certificates = CertificateState(
            device_cert=Path(certificates_data["device_cert"]),
            device_key=Path(certificates_data["device_key"]),
            ca_cert=Path(certificates_data["ca_cert"]),
            root_ca=Path(certificates_data["root_ca"]),
        )

    devices = {}

    for device_id, device_data in data.get("devices", {}).items():
        config_data = device_data.get("config", {})
        state_data = device_data.get("state", {})

        config = DeviceConfig(
            friendly_name=config_data["friendly_name"],
            account_id=config_data["account_id"],
            bridge_gateware_id=config_data["bridge_gateware_id"],
            device_id=config_data["device_id"],
            device_uuid=config_data["device_uuid"],
            udn=config_data["udn"],
            fingerprint=config_data["fingerprint"],
            mqtt_endpoint=config_data["mqtt_endpoint"],
        )

        device_state = DeviceState(
            power=state_data.get("power"),
            mode=state_data.get("mode"),
            brightness=state_data.get("brightness"),
            temperature=state_data.get("temperature"),
            rgb=(
                tuple(state_data["rgb"])
                if state_data.get("rgb") is not None
                else None
            ),
        )

        devices[device_id] = Device(
            config=config,
            state=device_state,
        )

    return AppState(
        certificates=certificates,
        devices=devices,
        provisioned=data.get("provisioned", False),
    )


def save_state(path: Path, state: AppState) -> None:
    """Save application state to a YAML file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": CURRENT_VERSION,
        "provisioned": state.provisioned,
        "certificates": (
            {
                "device_cert": str(state.certificates.device_cert),
                "device_key": str(state.certificates.device_key),
                "ca_cert": str(state.certificates.ca_cert),
                "root_ca": str(state.certificates.root_ca),
            }
            if state.certificates is not None
            else None
        ),
        "devices": {
            device_id: {
                "config": {
                    "friendly_name": device.config.friendly_name,
                    "account_id": device.config.account_id,
                    "bridge_gateware_id": device.config.bridge_gateware_id,
                    "device_id": device.config.device_id,
                    "device_uuid": device.config.device_uuid,
                    "udn": device.config.udn,
                    "fingerprint": device.config.fingerprint,
                    "mqtt_endpoint": device.config.mqtt_endpoint,
                },
                "state": {
                    "power": device.state.power,
                    "mode": device.state.mode,
                    "brightness": device.state.brightness,
                    "temperature": device.state.temperature,
                    "rgb": device.state.rgb,
                }

            }
            for device_id, device in state.devices.items()
        },
    }

    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def save_device_state(
        path: Path,
        device_id: str,
        device_state: DeviceState,
) -> None:
    """Update only the state of a specific device in the application state file."""

    if not path.exists():
        raise FileNotFoundError(f"State file does not exist: {path}")

    with path.open("r") as f:
        data = yaml.safe_load(f) or {}

    devices = data.setdefault("devices", {})

    if device_id not in devices:
        raise KeyError(f"Device '{device_id}' not found in state file")

    devices[device_id]["state"] = {
        "power": device_state.power,
        "mode": device_state.mode,
        "brightness": device_state.brightness,
        "temperature": device_state.temperature,
        "rgb": (
            list(device_state.rgb)
            if device_state.rgb is not None
            else None
        ),
        "connected": device_state.connected,
    }

    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def save_certificates(
        certificate_dir: Path,
        device_cert: str,
        device_key: str,
        ca_cert: str,
        root_ca: str,
) -> None:
    """Write provisioned certificates to the configured certificate directory."""

    certificate_dir.mkdir(parents=True, exist_ok=True)

    (certificate_dir / "device.crt").write_text(device_cert)
    (certificate_dir / "device.key").write_text(device_key)
    (certificate_dir / "ca.crt").write_text(ca_cert)
    (certificate_dir / "root-ca.crt").write_text(root_ca)
    os.chmod(certificate_dir / "device.key", 0o600)


def clear_state(path) -> None:
    """Clear the application state."""
    path.unlink(missing_ok=True)
