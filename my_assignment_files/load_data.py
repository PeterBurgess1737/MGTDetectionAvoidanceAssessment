import csv
import pathlib

import random


def load_data(logging: bool = False):
    data = {
        "human": [],
        "machine": []
    }

    skipped_rows_numbers = []

    with open(pathlib.Path("my_assignment_files/data/data.csv"), "r", encoding="UTF-8") as f:
        # Read as a csv file
        csvreader = csv.reader(f, quotechar='"')

        # Skip header row
        next(csvreader)

        # Parse each row
        index = 1
        while True:
            try:
                row = next(csvreader)
                text = row[0]
                source = row[1]

                if source.strip().lower() == "human":
                    data["human"].append(text)
                else:
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
            print("Loaded", len(data["human"]) + len(data["machine"]))

    random.seed(0)

    data["human"] = random.sample(data["human"], 100)
    data["machine"] = random.sample(data["machine"], 100)

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
