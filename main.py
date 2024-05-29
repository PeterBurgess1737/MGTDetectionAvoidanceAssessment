import importlib.util
import json
import pathlib
import shutil
import socket
import subprocess
import sys
from datetime import datetime

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


def create_save(load_data_filename: str,
                paraphraser_file: str, paraphraser_conda_env: str,
                ai_detector_file: str, ai_detector_conda_env: str,
                combined_data: dict) -> None:
    """
    Creates a save directory.
    Saves the results from the current to a file.
    Then copies over the necessary files to recreate the results.
    """

    print("create_save - Creating save directory")
    save_dir_name = f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
    save_path = pathlib.Path("results/" + save_dir_name).resolve()
    save_path.mkdir(parents=True, exist_ok=True)

    # Writing the results to a file
    print("create_save - Writing results to a file")
    with open(save_path / "paraphrased_results.json", "w") as f:
        f.write(json.dumps(combined_data))

    # Copying over some files to a save directory
    print("create_save - Copying over python files")
    python_file_path = save_path / "python_file_save"
    python_file_path.mkdir(parents=True, exist_ok=True)

    # The load data file
    load_data_filepath = pathlib.Path(load_data_filename).resolve()
    shutil.copy(load_data_filepath, python_file_path / load_data_filepath.name)

    # The paraphraser_file
    paraphraser_filepath = pathlib.Path(paraphraser_file).resolve()
    shutil.copy(paraphraser_filepath, python_file_path / paraphraser_filepath.name)

    # The ai_detector_file
    ai_detector_filepath = pathlib.Path(ai_detector_file).resolve()
    shutil.copy(ai_detector_filepath, python_file_path / ai_detector_filepath.name)

    # Copying over the conda environment yaml files
    print("create_save - Copying over conda environment files")
    conda_path = save_path / "conda_environment_save"
    conda_path.mkdir(parents=True, exist_ok=True)

    # The paraphraser conda environment
    paraphraser_yaml_file = conda_path / f"{paraphraser_conda_env}_environment.yaml"
    subprocess.run(f"conda env export --name \"{paraphraser_conda_env}\" --file \"{paraphraser_yaml_file}\"",
                   shell=True, check=True)

    # The ai detector conda environment
    ai_detector_yaml_file = conda_path / f"{ai_detector_conda_env}_environment.yaml"
    subprocess.run(f"conda env export --name \"{ai_detector_conda_env}\" --file \"{ai_detector_yaml_file}\"",
                   shell=True, check=True)

    # Writing some extra information
    print("create_save - Writing execution command")
    with open(save_path / "execution_command.txt", "w") as f:
        print(f"python {' '.join(sys.argv)}", file=f)


def main(load_data_filename: str,
         paraphraser_file: str, paraphraser_conda_env: str,
         ai_detector_file: str, ai_detector_conda_env: str,
         timeout_when_accepting_connections: int = 5):
    # Pretend the file pointed to by load_data_file is a module and load it
    print("Loading the load_data function")
    load_data_filepath = pathlib.Path(load_data_filename).resolve()
    module_name = load_data_filepath.stem
    spec = importlib.util.spec_from_file_location(module_name, load_data_filename)
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
    sock.settimeout(timeout_when_accepting_connections)
    try:
        paraphraser_sock, _paraphraser_address = sock.accept()
    except socket.timeout:
        print("Timed out when attempting to accept the paraphraser connection request")
        print("Either the paraphraser took too long to start or crashed")
        return
    sock.settimeout(None)

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
    sock.settimeout(timeout_when_accepting_connections)
    try:
        ai_detector_sock, _ai_detector_address = sock.accept()
    except socket.timeout:
        print("Timed out when attempting to accept the AI detector connection request")
        print("Either the AI detector took too long to start or crashed")
        return
    sock.settimeout(None)

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

    # Saving everything
    create_save(load_data_filename,
                paraphraser_file, paraphraser_conda_env,
                ai_detector_file, ai_detector_conda_env,
                combined_data)

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

    parser.add_argument(
        "--timeout-when-accepting-connections",
        default=5,
        type=int,
        help="The maximum amount of time the main handler will wait when accepting helper connections.",
        dest="timeout_when_accepting_connections",
    )

    args = parser.parse_args()

    main(args.load_data_file,
         args.paraphraser_file, args.paraphraser_conda_env,
         args.ai_detector_file, args.ai_detector_conda_env,
         timeout_when_accepting_connections=args.timeout_when_accepting_connections)
