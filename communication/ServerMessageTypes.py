import socket
import struct

from .BaseMessageType import BaseMessageType
from .Message import Message
from .read_length_then_data_from import read_length_then_data_from


def _DATA_read_rest_of_message_from(sock: socket.socket) -> Message:
    data_bytes = read_length_then_data_from(sock)

    string = data_bytes.decode("UTF-8")

    return Message(ServerMessageTypes.DATA, string)


def _DATA_create_message_with(data: str) -> bytes:
    data_bytes = data.encode("UTF-8")
    header_bytes = struct.pack("!BI", ServerMessageTypes.DATA.value, len(data_bytes))
    message_bytes = header_bytes + data_bytes

    return message_bytes


def _FINISH_read_rest_of_message_from(sock: socket.socket) -> Message:
    return Message(ServerMessageTypes.FINISH, None)


def _FINISH_create_message_with() -> bytes:
    message_bytes = struct.pack("!B", ServerMessageTypes.FINISH.value)

    return message_bytes


class ServerMessageTypes(BaseMessageType):
    """
    The types of messages sent by the main handler.
    This value is seen as the first byte of a message from the handler server as an unsigned char in network endianness.
    """

    DATA = 1, _DATA_read_rest_of_message_from, _DATA_create_message_with
    """
    Indicates that the message contains data.
    Following this is four bytes as an unsigned integer for the length of the data.
    Then the data, which is a string encoded as UTF-8.
    """

    FINISH = 2, _FINISH_read_rest_of_message_from, _FINISH_create_message_with
    """Indicates that this process should be terminated."""
