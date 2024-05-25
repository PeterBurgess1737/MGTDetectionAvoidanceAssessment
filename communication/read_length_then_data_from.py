import socket
import struct


def read_length_then_data_from(sock: socket.socket) -> bytes:
    """
    Reads four bytes from the socket for the length of the data to read.
    Then reads that many bytes from the socket.

    :param sock: The socket to read from.
    :return: The data bytes read, not including the length bytes.
    """

    data_length_bytes = bytes()
    while len(data_length_bytes) != 4:
        data_length_bytes += sock.recv(4 - len(data_length_bytes))
    data_length, = struct.unpack("!I", data_length_bytes)

    data_bytes = bytes()
    while len(data_bytes) != data_length:
        data_bytes += sock.recv(data_length - len(data_bytes))

    return data_bytes
