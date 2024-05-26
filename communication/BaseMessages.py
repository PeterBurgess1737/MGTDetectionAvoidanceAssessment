import socket
import struct
from enum import Enum
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:  # Preventing an import cycle with Message for type checking
    from .Message import Message


class BaseMessages(Enum):
    def __init__(self, value,
                 read_rest_of_message_from: Callable[[socket.socket], "Message"],
                 create_message: Callable[..., bytes]):
        """
        :param value: The indicator for the message type.
        :param read_rest_of_message_from:
            The function that takes a socket and returns the constructed message base on the indicator.
        :param create_message:
            The function that takes data necessary to create a message and returns the bytes for that message.
        """

        self._value_ = value
        self.read_rest_of_message_from = read_rest_of_message_from
        self.create_message = create_message

    @classmethod
    def from_int(cls, some_int) -> "BaseMessages":
        """
        Given an integer, convert it to a value from a BaseMessageType enum.

        :param some_int: The value to convert.
        :return: The converted value.
        :raises ValueError: If the given integer is not found in a BaseMessageType enum.
        """

        for value in cls:
            if value.value == some_int:
                return value

        raise ValueError(f"Unknown int for MessageTypes: {some_int}")

    @classmethod
    def read_indicator_from(cls, sock: socket.socket) -> "BaseMessages":
        """
        Given a socket, read a value from a BaseMessageType enum.
        :param sock: The socket to read.
        :return: The BaseMessageType enum value.
        """

        indicator_byte = sock.recv(1)
        indicator_int, = struct.unpack("!B", indicator_byte)
        return cls.from_int(indicator_int)
