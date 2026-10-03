import logging
import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

SRC_DIR = Path(__file__).resolve().parent.parent
CONFIG_FOLDER = SRC_DIR / "config"
CONFIG_PATH = CONFIG_FOLDER / "config.yaml"

load_dotenv(CONFIG_FOLDER / ".env")


@dataclass
class AwoxConfig:
    username: str
    password: str


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

    match data['logging']["level"].lower():
        case "debug":
            logging.basicConfig(level=logging.DEBUG)
        case "info":
            logging.basicConfig(level=logging.INFO)
        case "warning":
            logging.basicConfig(level=logging.WARNING)
        case "error":
            logging.basicConfig(level=logging.ERROR)
        case "fatal":
            logging.basicConfig(level=logging.FATAL)
        case "critical":
            logging.basicConfig(level=logging.CRITICAL)

    username = os.getenv("AWOX_USERNAME")
    password = os.getenv("AWOX_PASSWORD")

    if not username or not password or username == "awox@email.org":
        raise ValueError("AWOX_USERNAME and AWOX_PASSWORD are required. Edit config/.env to save them.")

    return AppConfig(
        awox=AwoxConfig(
            username=username,
            password=password,
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
