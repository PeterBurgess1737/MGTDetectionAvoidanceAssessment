import csv
import pathlib
import random

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

    with open(pathlib.Path("data/data.csv"), "r", encoding="UTF-8") as f:
        # Read as a csv file
        csvreader = csv.reader(f, quotechar='"')

        # Skip header row
        next(csvreader)

        # Parse each row
        index = 1
        while True:
            try:
                # Grab the row data
                row = next(csvreader)
                text = row[0]
                source = row[1].strip().lower()

                if source == "human":
                    if human_num >= human_max:
                        print(f"Skipped row {index} due to max number of human data encountered")
                        continue
                else:
                    if machine_num >= machine_max:
                        print(f"Skipped row {index} due to max number of machine data encountered")
                        continue

                # Check if there is too many tokens
                tokens = encoding.encode(text)
                if len(tokens) > 16000:
                    if logging:
                        print(f"Skipped row {index} due to too many tokens")
                        continue

                # If valid then add to the appropriate section
                if source == "human":
                    human_num += 1
                    data["human"].append(text)
                else:
                    machine_num += 1
                    data["machine"].append(text)

            except StopIteration:
                break

            except csv.Error as e:
                skipped_rows_numbers.append(index)
                if logging:
                    print(f"Skipped row {index} due to csv.Error: {e}")

            except IndexError as e:
                skipped_rows_numbers.append(index)
                if logging:
                    print(f"Skipped row {index} due to IndexError: {e}")
                    print(row)

            finally:
                index += 1

        if logging:
            print("Skipped", len(skipped_rows_numbers))
            print("Loaded", len(data["human"]) + len(data["machine"]), "total")
            print("\tHuman", len(data["human"]))
            print("\tMachine", len(data["machine"]))

    random.seed(0)

    return data


def main():
    # A way to test this function
    # A bunch of rows raise errors due to incorrect handling of the data
    # This appears to occur when there are newlines within the text field
    # For now at least I am ignoring the rows that are causing errors
    load_data(logging=True)
    # OUTPUT:
    # Skipped 17724
    # Loaded 798943


if __name__ == "__main__":
    main()
