import logging
import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv
from platformdirs import user_config_path, user_data_path

DEFAULTS = {
    "mqtt": {"endpoint": "a3n0qz5q2o66io.iot.us-east-1.amazonaws.com", "port": 443},
    "logging": {"level": "INFO"},
}


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


def get_dirs(home: str | None = None) -> tuple[Path, Path]:
    """Return (config_dir, data_dir) i.e. ~/.config/ and ~/.local/share/ ? """
    home = home or os.getenv("AWOX_HOME")
    if home:
        root = Path(home).expanduser().resolve()
        return root, root
    return user_config_path("awox"), user_data_path("awox")


def _merge(base: dict, extra: dict | None) -> dict:
    out = dict(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            out[k] = _merge(base[k], v)
        else:
            out[k] = v
    return out


def _resolve(value: str | None, base: Path, default: Path) -> Path:
    # return absolute path from value or default
    if not value:
        return default
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def load_config(home: str | None = None) -> AppConfig:
    config_dir, data_dir = get_dirs(home)
    load_dotenv(config_dir / ".env")  # real env vars still win

    user_file = config_dir / "config.yaml"
    user = yaml.safe_load(user_file.read_text()) if user_file.exists() else {}
    data = _merge(DEFAULTS, user)

    try:
        loglevel = data["logging"]["level"]
    except KeyError:
        loglevel = "Warning"

    match loglevel.lower():
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
        case _:
            logging.basicConfig(level=logging.WARNING)
            logging.warning("Logging level value not recognized")

    username = os.getenv("AWOX_USERNAME")
    password = os.getenv("AWOX_PASSWORD")

    if not username or not password or username == "awox@email.org":
        raise ValueError(
            f"AWOX_USERNAME and AWOX_PASSWORD are required. "
            f"Run `awox --init`, or put them in {config_dir / '.env'}, or export them.."
        )

    storage = data.get("storage", {})
    return AppConfig(
        awox=AwoxConfig(username=username, password=password),
        mqtt=MqttConfig(**data["mqtt"]),
        storage=StorageConfig(
            state_file=_resolve(storage.get("state_file"), config_dir, data_dir / "state.yaml"),
            certificate_directory=_resolve(storage.get("certificate_directory"), config_dir, data_dir / "certs"),
        ),
    )
