import socket

from Logger import Logger


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
