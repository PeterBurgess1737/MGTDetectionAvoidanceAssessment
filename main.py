"""
What do we need?

Well we need to load the data.
This will be a dictionary with two keys, 'human' and 'machine'.
The values will be a list of strings for texts.

We need to start the paraphraser helper and connect to it.
Then send each message in a sequence and get the result.
Once all messages have been sent then tell it to finish.

Then we need to start the AI detector and connect to it.
Send each text in a sequence and get the result.
Then tell it to finish.

Finally, write all the data to a json file for further processing.
"""

import importlib.util
import json
import pathlib
import socket
import struct
import subprocess
import sys

from communication import ParaphraserMessageTypes, ServerMessageTypes


def start_process(command):
    process = subprocess.Popen(
        command,
        shell=True
    )

    return process


def main(load_data_file: str,
         paraphraser_file: str, paraphraser_conda_env: str,
         ai_detector_file: str, ai_detector_conda_env: str):
    # Pretend the file pointed to by load_data_file is a module and load it
    print("Loading the load_data function")
    filepath = pathlib.Path(load_data_file).resolve()
    module_name = filepath.stem
    spec = importlib.util.spec_from_file_location(module_name, load_data_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Then get the load data function
    load_data = getattr(module, "load_data")

    # Then load the data
    print("Loading the data")
    data = load_data()

    # Creating a socket that the helpers can connect to for communication
    print("Crating the socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 8080))
    sock.listen()

    # Starting the paraphraser helper
    print("Starting the paraphraser helper")
    command = f"conda run -n {paraphraser_conda_env} python {paraphraser_file}"
    process = start_process(command)

    # Accepting the connection to the paraphraser helper
    print("Accepting the paraphraser connection")
    paraphraser_sock, _paraphraser_address = sock.accept()

    # Communication time

    paraphrased_data = {}

    # Sending strings and receiving the results from the paraphraser
    print("Paraphrasing everything")
    for key in data.keys():
        paraphrased_data[key] = []

        print("Paraphrasing: " + key)
        for i, string in enumerate(data[key]):
            # Sending the string
            print("Sending: '" + string[:30] + "'")
            string_bytes = string.encode("UTF-8")
            bytes_to_send = bytes()
            bytes_to_send += struct.pack("!BI", ServerMessageTypes.DATA.value, len(string_bytes))
            bytes_to_send += string.encode("UTF-8")
            paraphraser_sock.sendall(bytes_to_send)

            # Receiving the paraphrased string
            print("Waiting for response")
            indicator = ParaphraserMessageTypes.read_indicator_from(paraphraser_sock)
            paraphrase_result = indicator.read_rest_of_message_from(paraphraser_sock)
            paraphrased_data[key].append(paraphrase_result.data)
            print("Received: '" + paraphrase_result.data[:30] + "'")

    # Finally tell the paraphraser to finish
    print("Tell the paraphraser to finish")
    bytes_to_send = bytes()
    bytes_to_send += struct.pack("!B", ServerMessageTypes.FINISH.value)
    paraphraser_sock.sendall(bytes_to_send)

    # Wait for the paraphraser to terminate
    print("Waiting for the paraphraser to terminate")
    process.wait()

    # Writing the results to a file
    print("Writing to a file")
    with open("paraphrased_results.json", "w") as f:
        f.write(json.dumps(paraphrased_data))

    print("All done")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-ldf", "--load-data-file",
        type=str,
        required=True,
        help="The python file containing a function called `load_data`.",
        dest="load_data_file",
    )

    parser.add_argument(
        "-pf", "--paraphraser-file",
        type=str,
        required=True,
        help="The python file to be run to setup the paraphraser helper.",
        dest="paraphraser_file"
    )
    parser.add_argument(
        "-pce", "--paraphraser-conda-env",
        type=str,
        required=True,
        help="The name of the conda environment to run the paraphraser helper in.",
        dest="paraphraser_conda_env"
    )

    parser.add_argument(
        "-aidf", "--ai-detector-file",
        type=str,
        required=True,
        help="The python file to be run to setup the AI detector helper.",
        dest="ai_detector_file"
    )
    parser.add_argument(
        "-aidce", "--ai-detector-conda-env",
        type=str,
        required=True,
        help="The name of the conda environment to run the AI detector helper in.",
        dest="ai_detector_conda_env"
    )

    args = parser.parse_args()

    main(args.load_data_file,
         args.paraphraser_file, args.paraphraser_conda_env,
         args.ai_detector_file, args.ai_detector_conda_env)
