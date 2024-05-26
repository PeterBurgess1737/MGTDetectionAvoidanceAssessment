import socket
import struct

from .BaseMessageType import BaseMessageType
from .Message import Message


def _DATA_read_rest_of_message_from(sock: socket.socket) -> Message:
    percentage_as_float_bytes = bytes()
    while len(percentage_as_float_bytes) != 4:
        percentage_as_float_bytes += sock.recv(4 - len(percentage_as_float_bytes))
    percentage_as_float, = struct.unpack("!f", percentage_as_float_bytes)

    return Message(AIDetectorMessages.DATA, percentage_as_float)


def _DATA_create_message_with(data: float) -> bytes:
    message_bytes = struct.pack("!Bf", AIDetectorMessages.DATA.value, data)

    return message_bytes


class AIDetectorMessages(BaseMessageType):
    """
    The types of messages sent by the main handler.
    This value is seen as the first byte of a message from the AI detector server as an unsigned char in network
    endianness.
    """

    DATA = 1, _DATA_read_rest_of_message_from, _DATA_create_message_with
    """
    Indicates that the message contains data.
    Following this is four bytes as a float.
    """
