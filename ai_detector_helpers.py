from typing import Callable

from communication import AIDetectorMessages, ServerMessages, connect_to_server


def ai_detector_server(detector_function: Callable[[str], float],
                       server_address: str = "localhost", server_port: int = 8080):
    """
    A helper function for the AI detector.
    Performs the task of receiving data from the server, calculating the change of it being AI generated and sending the
     result back.
    If a terminate message is received, terminate.

    Similar to the paraphraser, this is a very simple implementation.

    If calculating the percentage chance of a message being AI generated is simple, it can be passed as a function that
     returns a float in the range of 0 to 1.

    If that is not the case, then the general flow of this helper can be seen in its implementation.

    :param detector_function: A function that takes text and returns a change of it being AI generated.
    :param server_address: The address of the handler server to connect to.
    :param server_port: The port of the handler server to connect to.
    """

    # Connect to the handler server
    sock = connect_to_server(server_address, server_port)

    while True:
        # Receive a message from the handler sever
        indicator = ServerMessages.read_indicator_from(sock)
        message = indicator.read_rest_of_message_from(sock)

        if message.type == ServerMessages.DATA:
            # Get the string
            string = message.data

            # Calculate the change of it being AI generated
            percentage_change_ai = detector_function(string)

            # Send the result back to the handler server
            bytes_to_send = AIDetectorMessages.DATA.create_message(percentage_change_ai)
            sock.sendall(bytes_to_send)

            # Repeat
            continue

        else:
            # Because message.type is FINISH we have nothing else to do but terminate
            break

    sock.close()
