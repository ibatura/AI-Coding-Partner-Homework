"""Base agent class providing shared messaging utilities for all pipeline agents."""

import json
import logging
import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path


class BaseAgent(ABC):
    """Abstract base class for all pipeline agents."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        """Configure structured audit logging to stdout."""
        logger = logging.getLogger(self.name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    def process_message(self, message: dict) -> dict:
        """Process an incoming message. Must be implemented by subclasses."""

    def read_message(self, filepath: str) -> dict:
        """Read and parse a JSON message from file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_message(self, message: dict, directory: str) -> str:
        """Write a JSON message to directory. Returns the written filepath."""
        Path(directory).mkdir(parents=True, exist_ok=True)
        transaction_id = message.get("data", {}).get("transaction_id", str(uuid.uuid4()))
        filename = f"{transaction_id}.json"
        filepath = str(Path(directory) / filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(message, f, indent=2, default=str)
        return filepath

    def create_message_envelope(
        self, data: dict, target_agent: str, message_type: str = "transaction"
    ) -> dict:
        """Build a standard message envelope."""
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_agent": self.name,
            "target_agent": target_agent,
            "message_type": message_type,
            "data": data,
        }

    def mask_pii(self, text: str) -> str:
        """Mask account number patterns in log output (e.g., ACC-1001 → ACC-***1)."""
        return re.sub(r"(ACC-)(\d+)", lambda m: f"ACC-***{m.group(2)[-1]}", str(text))
