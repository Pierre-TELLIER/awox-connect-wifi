from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class CertificateState:
    device_cert: Path
    device_key: Path
    ca_cert: Path
    root_ca: Path


@dataclass
class DeviceState:
    account_id: str | None = None
    bridge_gateware_id: str | None = None
    device_id: str | None = None
    device_uuid: str | None = None
    udn: str | None = None
    fingerprint: str | None = None
    mqtt_endpoint: str | None = None


@dataclass
class AppState:
    certificates: CertificateState | None = None
    devices: dict[str, DeviceState] = field(default_factory=dict)
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

    certificates_data = data.get("certificates")

    certificates = None
    if certificates_data:
        certificates = CertificateState(
            device_cert=Path(certificates_data["device_cert"]),
            device_key=Path(certificates_data["device_key"]),
            ca_cert=Path(certificates_data["ca_cert"]),
            root_ca=Path(certificates_data["root_ca"]),
        )

    devices = {
        device_id: DeviceState(**device_data)
        for device_id, device_data in data.get("devices", {}).items()
    }

    return AppState(
        certificates=certificates,
        devices=devices,
        provisioned=data.get("provisioned", False),
    )


def save_state(path: Path, state: AppState) -> None:
    """Save application state to a YAML file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
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
                "account_id": device.account_id,
                "bridge_gateware_id": device.bridge_gateware_id,
                "device_id": device.device_id,
                "device_uuid": device.device_uuid,
                "udn": device.udn,
                "fingerprint": device.fingerprint,
                "mqtt_endpoint": device.mqtt_endpoint,
            }
            for device_id, device in state.devices.items()
        },
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
