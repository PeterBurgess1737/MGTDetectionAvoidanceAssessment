"""
Contains Enums for the different types of messages sent between the handler server and any helpers.
"""


from enum import Enum


class ServerMessageTypes(Enum):
    """
    The types of messages sent by the main handler.
    This value is seen as the first byte of a message from the handler server as an unsigned char in network endianness.
    """

    DATA = 1
    """
    Indicates that the message contains data.
    Following this is four bytes as an unsigned integer for the length of the data.
    Then the data, which is a string encoded as UTF-8.
    """
    FINISH = 2
    """Indicates that this process should be terminated."""

    @classmethod
    def from_int(cls, some_int) -> 'ServerMessageTypes':
        for value in cls:
            if value.value == some_int:
                return value

        raise ValueError(f"Unknown int for MessageTypes: {some_int}")


class ParaphraserMessageTypes(Enum):
    """
    The types of messages sent by the main handler.
    This value is seen as the first byte of a message from the paraphraser server as an unsigned char in network
    endianness.
    """

    DATA = 1
    """
    Indicates that the message contains data.
    Following this is four bytes as an unsigned integer for the length of the data.
    Then the data, which is a string encoded as UTF-8.
    The same as what the server sends to the paraphraser.
    """
