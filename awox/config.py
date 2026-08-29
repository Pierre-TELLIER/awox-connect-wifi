import os
from dataclasses import dataclass
from pathlib import Path

import yaml
SRC_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SRC_DIR / "config" / "config.yaml"

@dataclass
class AwoxConfig:
    username: str
    password: str
    target_device_name: str


@dataclass
class MqttConfig:
    endpoint: str
    port: int

@dataclass
class StorageConfig:
    state_file: Path
    certificate_directory: Path

@dataclass
class AppConfig:
    awox: AwoxConfig
    mqtt: MqttConfig
    storage: StorageConfig



def resolve_config_path(value: str) -> Path:
    path = Path(value).expanduser()

    if path.is_absolute():
        return path

    return (CONFIG_PATH.parent / path).resolve()


def load_config() -> AppConfig:

    with CONFIG_PATH.open("r") as f:
        data = yaml.safe_load(f)

    return AppConfig(
        awox=AwoxConfig(
            username=data["awox"]["username"],
            password=data["awox"]["password"],
            target_device_name=data["awox"]["target_device_name"],
        ),
        mqtt=MqttConfig(
            endpoint=data["mqtt"]["endpoint"],
            port=data["mqtt"]["port"],
        ),
        storage=StorageConfig(
            state_file=resolve_config_path(
                data["storage"]["state_file"],
            ),
            certificate_directory=resolve_config_path(
                data["storage"]["certificate_directory"],
            ),
        ),
    )
