import socket
import struct
from dataclasses import dataclass
from typing import Union, Callable

from MessageTypes import ServerMessageTypes, ParaphraserMessageTypes
from Logger import Logger


@dataclass
class Message:
    """
    A simple class that contains information about a message from the handler server.
    That is the message type and any associated data as a string.
    """

    type: ServerMessageTypes
    """The type of the message."""
    data: Union[str, None]
    """Any data received from the handler."""


def connect_to_server(server_address: str = "localhost", server_port: int = 8080) -> socket.socket:
    """
    A helper function for the paraphraser.
    Attempts to connect to the handler server and return the socket object.

    :param server_address: The address of the handler server to connect to.
    :param server_port: The port of the handler server to connect to.
    :return: The socket object connected to the server.
    :raises TimeoutError: If the handler server cannot be reached.
    """

    Logger.log(f"Connecting to server at {server_address}:{server_port}")

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)

    # Attempt a connection to the server
    try:
        sock.connect((server_address, server_port))
    except TimeoutError as e:
        Logger.log(f"Connection to timed out.")
        raise e
    sock.settimeout(None)

    Logger.log(f"Connection successful")

    # All done
    return sock


def receive_message(sock: socket.socket) -> Message:
    """
    A helper function for the paraphraser.
    Attempts to receive a message from the handler.
    The message is returned as a Message object containing data if applicable.

    :param sock: The socket object connected to the server.
    :return: The received message.
    """

    Logger.log(f"Receiving message from handler server")

    # Receive the indicator from the handler server
    indicator_byte = sock.recv(1)
    indicator_int, = struct.unpack("!B", indicator_byte)
    indicator = ServerMessageTypes.from_int(indicator_int)

    Logger.log(f"Received indicator {indicator.name}")

    # If it is a finish message, then there is nothing else to do
    if indicator == ServerMessageTypes.FINISH:
        return Message(indicator, None)

    Logger.log("Reading length of data - ", end="")

    # If not then we need to find the length of the string to receive
    # This is the next four bytes as an unsigned integer
    string_length_bytes = bytes()
    while len(string_length_bytes) != 4:
        string_length_bytes += sock.recv(4 - len(string_length_bytes))
    string_length, = struct.unpack("!I", string_length_bytes)

    Logger.log(string_length)
    Logger.log(f"Reading data - ")

    # Now read the rest of the string data
    string_bytes = bytes()
    while len(string_bytes) != string_length:
        string_bytes += sock.recv(string_length - len(string_bytes))

    Logger.log("Done")

    # Convert the string to an actual string
    string = string_bytes.decode("UTF-8")

    # We are done
    return Message(indicator, string)


def send_paraphrased_string(sock: socket.socket, string: str) -> None:
    """
    A helper function for the paraphraser.
    Sends a string back to the handler server.

    :param sock: The socket object connected to the server.
    :param string: The string to send.
    """

    Logger.log(f"Sending string to handler server")

    bytes_to_send = bytes()
    bytes_to_send += struct.pack("!B", ParaphraserMessageTypes.DATA.value)
    bytes_to_send += struct.pack("!I", len(string))
    bytes_to_send += string.encode("UTF-8")
    sock.sendall(bytes_to_send)


def paraphraser_server(paraphrase_function: Callable[[str], str],
                       server_address: str = "localhost", server_port: int = 8080,
                       verbose: bool = True) -> None:
    """
    A helper function for the paraphraser.
    Performs the task of receiving data from the server, paraphrasing it and sending the result back.
    If a terminate message is received, terminate.

    This is a very simple paraphraser implementation.

    If the paraphrasing itself is simple, it can be passed as a function that takes the original text and returns a
    paraphrased version.

    If the paraphrasing is not simple, then the flow of this helper can be seen in its implementation.
    To make things easier, the code to receive messages and send results back can be seen above as their own functions.
    You can simply import from this file the functions.

    :param paraphrase_function: A function that takes the original text and returns a paraphrased version.
    :param server_address: The address of the handler server to connect to.
    :param server_port: The port of the handler server to connect to.
    :param verbose: If paraphraser should be verbose.
    """

    Logger.verbose = verbose

    Logger.log(f"Starting paraphraser server")

    # Connect to the handler server
    sock = connect_to_server(server_address, server_port)

    while True:
        # Receive a message from the handler sever
        message = receive_message(sock)

        if message.type == ServerMessageTypes.DATA:
            # Get the string
            string = message.data

            # Paraphrase it
            paraphrased_string = paraphrase_function(string)

            # Send it back to the handler server
            send_paraphrased_string(sock, paraphrased_string)

            # Repeat
            continue

        else:
            # Because message.type is FINISH we have nothing else to do but terminate
            break

    Logger.log("Terminating paraphraser server")
