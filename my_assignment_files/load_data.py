import pathlib

import pandas as pd
import tiktoken

# Should be the same as in gpt_paraphraser.py
MODEL = "gpt-3.5-turbo"

# The maximum amount of data to read
# Divide this by 2 to get the maximum for human and machine separately
MAX_DATA = 1000


def load_data(logging: bool = False):
    data = {
        "human": [],
        "machine": []
    }

    human_max = MAX_DATA // 2
    human_num = 0
    machine_max = MAX_DATA // 2
    machine_num = 0

    skipped_rows_numbers = []
    encoding = tiktoken.encoding_for_model(MODEL)

    df = pd.read_csv(pathlib.Path("my_assignment_files/data/data.csv"))
    df = df.sample(frac=1, random_state=1).reset_index(drop=True)

    for index, row in df.iterrows():
        source = row["source"].strip().lower()

        # Terminate if at max data
        if human_num >= human_max and machine_num >= machine_max:
            if logging:
                print("Max number of human and machine data encountered")
            break

        # Skip if reached max amount
        if source == "human":
            if human_num >= human_max:
                if logging:
                    print(f"Skipped row {index} due to max number of human data encountered")
                skipped_rows_numbers.append(index)
                continue
        else:
            if machine_num >= machine_max:
                if logging:
                    print(f"Skipped row {index} due to max number of machine data encountered")
                skipped_rows_numbers.append(index)
                continue

        text = row["text"]

        # Skip if there is too many tokens
        tokens = encoding.encode(text)
        if len(tokens) > 16000:
            if logging:
                print(f"Skipped row {index} due to too many tokens")
            skipped_rows_numbers.append(index)
            continue

        if source == "human":
            human_num += 1
            data["human"].append(text)
        else:
            machine_num += 1
            data["machine"].append(text)

    if logging:
        print("Skipped", len(skipped_rows_numbers))
        print("Loaded", len(data["human"]) + len(data["machine"]), "total")
        print("\tHuman", len(data["human"]))
        print("\tMachine", len(data["machine"]))

    return data


def main():
    # A way to test this function
    # A bunch of rows raise errors due to incorrect handling of the data
    # This appears to occur when there are newlines within the text field
    # For now at least I am ignoring the rows that are causing errors
    load_data(logging=True)


if __name__ == "__main__":
    main()
