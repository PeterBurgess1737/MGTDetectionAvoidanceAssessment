# Setting my up my files.

## The conda environment for `main.py`

Create the conda environment for the main file:

```shell
conda create env -f TopicsBase.yaml
```

## Setting up the data loader

The data I used can be downloaded from this link:
[human-vs-llm-text-corpus](https://www.kaggle.com/datasets/starblasters8/human-vs-llm-text-corpus).
There should be a file called `data.csv`.
This should be placed in the `data` directory.

The file [load_data.py](load_data.py) is used to load the data. It should be run with the main file conda environment
that is set up above.

## Setting up the paraphraser

Create the conda environment for the paraphraser:

```shell
conda env create -f gpt_env.yaml 
```

The file [gpt_paraphraser.py](gpt_paraphraser.py) contains the server for the paraphraser.
It should be run with the above conda environment.

## Setting up the AI detector

Clone the RADAR Repository.

```shell
git clone https://github.com/IBM/RADAR.git
```

Follow the instructions in [RADAR/readme.md](RADAR/README.md) to set up its conda environment.

Note: when attempting to install (May 2024) there were two conflicting package requirements that I encountered.
I fixed these by changing two lines:

```
From
     jupyter-core==4.5.0
To
     jupyter-core==4.6.0

From
     tokenizers==0.13.3
To
     tokenizers==0.12.1
```

The file [radar_detector.py](radar_detector.py) contains the server for the detector.
It should be run with the RADAR conda environment.

# Running what I used

Once the above steps have been taken.

The files:

- [gpt_paraphraser.py](gpt_paraphraser.py)
- [load_data.py](load_data.py)
- [radar_detector.py](radar_detector.py)

Should be copied to the main directory.

There is a bash file under the `commands` directory called `my_assignment.sh`.  
This contains the command I used to run the code.  
It should be run from the main repository directory, not in the `my_assignment_files` directory.
