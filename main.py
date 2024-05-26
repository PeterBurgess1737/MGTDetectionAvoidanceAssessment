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
import subprocess
import sys

from progress.bar import ChargingBar

from communication import AIDetectorMessages, ParaphraserMessages, ServerMessages


class MyBar(ChargingBar):
    suffix = "%(percent)d%% (elapsed %(elapsed)ss) (eta %(eta)ss)"


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

    # Where all the data is stored
    # Think of this like a table in a database where the keys are the column names
    combined_data = {
        # The original texts, both human and AI, from the given dataset
        "original_text": [],
        # A boolean value stating of the corresponding text is AI generated
        "is_ai": [],
        # The paraphrased version of the original text.
        "paraphrased_text": [],
        # The detection rate of the original text according to the AI text detector
        "original_detection": [],
        # The detection rate of the paraphrased text according to the AI text detector
        "paraphrased_detection": []
    }

    # Processing the given data to fit in this combined_data dictionary
    combined_data["original_text"].extend(data["human"])
    combined_data["original_text"].extend(data["machine"])
    combined_data["is_ai"].extend([False for _ in range(len(data["human"]))])
    combined_data["is_ai"].extend([True for _ in range(len(data["machine"]))])

    # We no longer need the original data
    del data

    # Fill the other entries with default values
    combined_data["paraphrased_text"].extend([None for _ in range(len(combined_data["original_text"]))])
    combined_data["original_detection"].extend([None for _ in range(len(combined_data["original_text"]))])
    combined_data["paraphrased_detection"].extend([None for _ in range(len(combined_data["original_text"]))])

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

    progress = MyBar(f"Paraphrasing", max=len(combined_data["original_text"]))

    # Sending strings and receiving the results from the paraphraser
    for i, string in enumerate(combined_data["original_text"]):
        # Sending the string
        bytes_to_send = ServerMessages.DATA.create_message(string)
        paraphraser_sock.sendall(bytes_to_send)

        # Receiving the paraphrased string
        indicator = ParaphraserMessages.read_indicator_from(paraphraser_sock)
        paraphrase_result = indicator.read_rest_of_message_from(paraphraser_sock)

        # Store it
        combined_data["paraphrased_text"][i] = paraphrase_result.data

        # Update the progress bar
        progress.next()

    # Done with the progress bar
    progress.finish()

    # Finally tell the paraphraser to finish
    print("Tell the paraphraser to finish")
    bytes_to_send = ServerMessages.FINISH.create_message()
    paraphraser_sock.sendall(bytes_to_send)

    # Wait for the paraphraser to terminate
    print("Waiting for the paraphraser to terminate")
    process.wait()
    # Close the socket
    paraphraser_sock.close()

    # Starting the AI detector helper
    print("Starting the AI detector helper")
    command = f"conda run -n {ai_detector_conda_env} python {ai_detector_file}"
    process = start_process(command)

    # Accepting the connection to the AI detector helper
    print("Accepting the AI detector connection")
    ai_detector_sock, _ai_detector_address = sock.accept()

    # Communication time

    progress = MyBar(f"Calculating AI percentages", max=len(combined_data["original_text"]))

    # Sending strings and receiving the results from the AI detector
    for i, (original_text, paraphrased_text) in \
            enumerate(zip(combined_data["original_text"], combined_data["paraphrased_text"])):
        # Send the original text
        bytes_to_send = ServerMessages.DATA.create_message(original_text)
        ai_detector_sock.sendall(bytes_to_send)

        # Receiving the result
        indicator = AIDetectorMessages.read_indicator_from(ai_detector_sock)
        ai_detector_result = indicator.read_rest_of_message_from(ai_detector_sock)

        # Store the result
        combined_data["original_detection"][i] = ai_detector_result.data

        # Send the paraphrased text
        bytes_to_send = ServerMessages.DATA.create_message(paraphrased_text)
        ai_detector_sock.sendall(bytes_to_send)

        # Receiving the result
        indicator = AIDetectorMessages.read_indicator_from(ai_detector_sock)
        ai_detector_result = indicator.read_rest_of_message_from(ai_detector_sock)

        # Store the result
        combined_data["paraphrased_detection"][i] = ai_detector_result.data

        # Update the progress bar
        progress.next()

    # Done with the progress bar
    progress.finish()

    # Finally tell the AI detector to finish
    print("Tell the AI detector to finish")
    bytes_to_send = ServerMessages.FINISH.create_message()
    ai_detector_sock.sendall(bytes_to_send)

    # Wait for the paraphraser to terminate
    print("Waiting for the AI detector to terminate")
    process.wait()
    # Close the socket
    ai_detector_sock.close()

    # Writing the results to a file
    print("Writing to a file")
    with open("paraphrased_results.json", "w") as f:
        f.write(json.dumps(combined_data))

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
