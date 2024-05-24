import socket
import struct
from typing import Callable

from communication import ParaphraserMessageTypes, ServerMessageTypes, connect_to_server


def send_paraphrased_string(sock: socket.socket, string: str) -> None:
    """
    A helper function for the paraphraser.
    Sends a string back to the handler server.

    :param sock: The socket object connected to the server.
    :param string: The string to send.
    """

    bytes_to_send = bytes()
    bytes_to_send += struct.pack("!B", ParaphraserMessageTypes.DATA.value)
    bytes_to_send += struct.pack("!I", len(string))
    bytes_to_send += string.encode("UTF-8")
    sock.sendall(bytes_to_send)


def paraphraser_server(paraphrase_function: Callable[[str], str],
                       server_address: str = "localhost", server_port: int = 8080) -> None:
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
    """

    # Connect to the handler server
    sock = connect_to_server(server_address, server_port)

    while True:
        # Receive a message from the handler sever
        indicator = ServerMessageTypes.read_indicator_from(sock)
        message = indicator.read_rest_of_message_from(sock)

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

    sock.close()
