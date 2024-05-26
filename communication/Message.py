from typing import Any

from .BaseMessages import BaseMessages


class Message:
    def __init__(self, type_: BaseMessages, data: Any) -> None:
        self.type: BaseMessages = type_
        """The type of the message."""

        self.data: Any = data
        """Any data required for the message."""

    def __str__(self) -> str:
        return "Message(type=" + self.type.name + ", data='" + str(self.data) + "')"
