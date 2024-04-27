import json
import os

from typing import Dict, List
from typing_extensions import Literal

_keys = Literal["human", "machine"]


def load_test_data(test_data_path: str) -> Dict[_keys, List[str]]:
    """
    Load test data from `test_data_path` in a more usable format.

    See function code for json format.

    :param test_data_path: The path to the test data file.
    :return: The test data dictionary.
    :raises ValueError: If `test_data_path` is not a valid path.
    """

    """
    Expects a json file in the format:
    
    {
        "texts": [
            "Some text ...",
            "Some more text ...",
            "Even more text ...",
        ],
        "label": [
            0,  # Human
            1,  # Machine
            0,
        ]
    }
    """

    if not test_data_path.endswith(".json"):
        raise ValueError(f"Path '{test_data_path}' must end with .json")

    if not os.path.exists(test_data_path):
        raise ValueError(f"Path '{test_data_path}' does not exist")

    with open(test_data_path, "r") as f:
        data = f.read()

    data = json.loads(data)

    to_return: Dict[_keys, List[str]] = {
        "human": [],
        "machine": []
    }

    for index, is_machine in enumerate(data["label"]):
        if is_machine:
            to_return["machine"].append(data["text"][index])
        else:
            to_return["human"].append(data["text"][index])

    return to_return
