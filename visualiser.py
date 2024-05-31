import json
import os
import pathlib
import warnings
from typing import List, Tuple

import matplotlib.pyplot as plt
import seaborn as sns

_Data = Tuple[List[float], List[float]]


def select_results(result_paths: List[pathlib.Path]) -> pathlib.Path:
    result_paths.sort()

    if len(result_paths) == 1:
        return result_paths[0]

    print(f"Use latest path '{result_paths[-1]}'?")
    while True:
        choice = input("[y]/n - ").lower()
        if choice == "y" or choice == "":
            return result_paths[-1]
        if choice == "n":
            break

        print("Invalid choice")

    num_paths = len(result_paths)
    padding = len(str(num_paths))

    if len(result_paths) > 9:
        print()

        for i, path in enumerate(result_paths[:5], start=1):
            print(f"{str(i).rjust(padding)}: {path}")

        print("...")

        for i, path in enumerate(result_paths[-5:], start=num_paths - 4):
            print(f"{str(i).rjust(padding)}: {path}")

        options = ["1", "2", "3", "4", "5"] + [str(i) for i in range(num_paths - 4, num_paths + 1)]

        print("Chose a path from the list or enter nothing to display all")
        while True:
            choice = input("> ")
            if not choice:
                break
            if choice in options:
                return result_paths[int(choice) - 1]

            print("Invalid choice")

    print()

    options = [str(i) for i in range(1, num_paths + 1)]

    for i, path in enumerate(result_paths, start=1):
        print(f"{str(i).rjust(padding)}: {path}")

    print("Chose a path from the list")
    while True:
        choice = input("> ")
        if choice in options:
            break

        print("Invalid choice")

    return result_paths[int(choice) - 1]


def plot_as_box_plots(pre_paraphrased_data: _Data, post_paraphrased_data: _Data, plots_path: pathlib.Path) -> None:
    figure, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 6), sharey="all")

    axes[0].boxplot(pre_paraphrased_data, widths=0.3, showfliers=True)
    axes[0].set_title("Original Texts")
    axes[0].set_xticklabels(["Human", "Machine"])
    axes[0].set_ylim(0, 1)
    axes[0].set_ylabel("RADAR - Machine Generated Probability")

    axes[1].boxplot(post_paraphrased_data, widths=0.3, showfliers=True)
    axes[1].set_title("Paraphrased Texts")
    axes[1].set_xticklabels(["Human", "Machine"])
    axes[1].set_ylim(0, 1)

    plt.tight_layout()

    plt.savefig(plots_path / "box_plot.png", format="png")


def plot_as_histogram(pre_paraphrased_data: _Data, post_paraphrased_data: _Data, plots_path: pathlib.Path) -> None:
    figure, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharey="all")

    axes[0].hist(pre_paraphrased_data, bins=10, label=["Human", "Machine"])
    axes[0].set_title("Original Texts")
    axes[0].set_ylabel("Frequency")
    axes[0].set_xlabel("RADAR - Machine Generated Probability")
    axes[0].legend(loc="upper left")

    axes[1].hist(post_paraphrased_data, bins=10, label=["Human", "Machine"])
    axes[1].set_title("Paraphrased Texts")
    axes[1].legend(loc="upper left")

    plt.tight_layout()

    plt.savefig(plots_path / "histogram.png", format="png")


def plot_as_probability_density(pre_paraphrased_data: _Data, post_paraphrased_data: _Data,
                                plots_path: pathlib.Path) -> None:
    figure, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharey="all")

    sns.kdeplot(pre_paraphrased_data[0], ax=axes[0], label="Human", fill=True, clip=(0, 1))
    sns.kdeplot(pre_paraphrased_data[1], ax=axes[0], label="Machine", fill=True, clip=(0, 1))
    axes[0].set_title("Original Texts")
    axes[0].set_ylabel("Relative Probability")
    axes[0].set_xlabel("RADAR - Machine Generated Probability")
    axes[0].legend(loc="upper left")
    axes[0].set_xlim(0, 1)

    sns.kdeplot(post_paraphrased_data[0], ax=axes[1], label="Human", fill=True, clip=(0, 1))
    sns.kdeplot(post_paraphrased_data[1], ax=axes[1], label="Machine", fill=True, clip=(0, 1))
    axes[1].set_title("Paraphrased Texts")
    axes[1].legend(loc="upper left")
    axes[1].set_xlim(0, 1)

    plt.tight_layout()

    plt.savefig(plots_path / "normal.png", format="png")


def main():
    warnings.simplefilter(action="ignore", category=FutureWarning)

    plt.switch_backend("Agg")

    print("Searching for results")
    results_directory = pathlib.Path("results")

    if not results_directory.exists():
        print("No results directory found")
        return

    result_paths = []
    for _path in os.listdir(results_directory):
        potential_result_path = results_directory / _path

        if potential_result_path.is_dir():
            result_paths.append(potential_result_path)

    if not result_paths:
        print("No results found in results directory")
        return

    print(f"{len(result_paths)} results found")

    result_paths.sort()

    working_results_path = select_results(result_paths)

    print(f"Using results {working_results_path}")

    results_data_path = working_results_path / "paraphrased_results.json"

    if not results_data_path.exists():
        print("No results data found")
        return

    with open(results_data_path, "r") as f:
        results_data = json.loads(f.read())

    pre_paraphrased_human = []
    pre_paraphrased_machine = []
    post_paraphrased_human = []
    post_paraphrased_machine = []

    for i, (pre_paraphrased_percentage, post_paraphrased_percentage) in \
            enumerate(zip(results_data["original_detection"], results_data["paraphrased_detection"])):
        if results_data["is_ai"][i]:
            pre_paraphrased_machine.append(pre_paraphrased_percentage)
            post_paraphrased_machine.append(post_paraphrased_percentage)
        else:
            pre_paraphrased_human.append(pre_paraphrased_percentage)
            post_paraphrased_human.append(post_paraphrased_percentage)

    pre_paraphrased_data = (pre_paraphrased_human, pre_paraphrased_machine)
    post_paraphrased_data = (post_paraphrased_human, post_paraphrased_machine)

    plots_path = working_results_path / "plots"
    plots_path.mkdir(exist_ok=True)

    plot_as_box_plots(pre_paraphrased_data, post_paraphrased_data, plots_path)
    plot_as_histogram(pre_paraphrased_data, post_paraphrased_data, plots_path)
    plot_as_probability_density(pre_paraphrased_data, post_paraphrased_data, plots_path)


if __name__ == "__main__":
    main()
