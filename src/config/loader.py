from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ServerConfig:
    port: int
    max_workers: int


@dataclass(frozen=True)
class ModelConfig:
    name: str
    threshold: float


@dataclass(frozen=True)
class AppConfig:
    server: ServerConfig
    model: ModelConfig


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "config.yaml"


def load_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path or os.getenv("SMART_SENTRY_CONFIG") or _default_config_path())
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    server_data = data.get("server", {})
    model_data = data.get("model", {})

    port = int(server_data.get("port", 50051))
    max_workers = int(server_data.get("max_workers", 10))
    model_name = str(model_data.get("name", "Falconsai/nsfw_image_detection"))
    threshold = float(model_data.get("threshold", 0.75))

    if port <= 0:
        raise ValueError("server.port must be greater than 0")
    if max_workers <= 0:
        raise ValueError("server.max_workers must be greater than 0")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("model.threshold must be between 0.0 and 1.0")

    return AppConfig(
        server=ServerConfig(port=port, max_workers=max_workers),
        model=ModelConfig(name=model_name, threshold=threshold),
    )
