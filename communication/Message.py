from dataclasses import dataclass
from typing import Any

from .BaseMessageType import BaseMessageType


@dataclass
class Message:
    type: BaseMessageType
    """The type of the message."""

    data: Any
    """Any data required for the message."""
