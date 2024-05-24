import socket

from .BaseMessageType import BaseMessageType
from .Message import Message
from .read_length_then_data_from import read_length_then_data_from


def _DATA_read_rest_of_message_from(sock: socket.socket) -> Message:
    data_bytes = read_length_then_data_from(sock)

    string = data_bytes.decode("UTF-8")

    return Message(ServerMessageTypes.DATA, string)


def _FINISH_read_rest_of_message_from(sock: socket.socket) -> Message:
    return Message(ServerMessageTypes.FINISH, None)


class ServerMessageTypes(BaseMessageType):
    """
    The types of messages sent by the main handler.
    This value is seen as the first byte of a message from the handler server as an unsigned char in network endianness.
    """

    DATA = 1, _DATA_read_rest_of_message_from
    """
    Indicates that the message contains data.
    Following this is four bytes as an unsigned integer for the length of the data.
    Then the data, which is a string encoded as UTF-8.
    """

    FINISH = 2, _FINISH_read_rest_of_message_from
    """Indicates that this process should be terminated."""
