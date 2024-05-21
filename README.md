# MGTDetectionAvoidanceAssessment

The code repository for the Topics In Computer Science course I am taking.  
This readme contains information about the specifics of how to use certain components alongside general thoughts.

## Table of Contents

<!-- TOC -->
* [MGTDetectionAvoidanceAssessment](#mgtdetectionavoidanceassessment)
  * [Table of Contents](#table-of-contents)
  * [Initial Idea](#initial-idea)
<!-- TOC -->

## Initial Idea

I intended for this repository to be a way to run a dataset of texts, both machine generated and human written, through
a paraphraser of some kind, then through an AI text detector of some kind.
With the end goal of being easy to set up and use, even when swapping out components.

The main handler script is designed to run with pure python, no extra packages required.
However, the paraphraser and AI text detector might need packages to work.
When initially testing this out, I found that it was common for requirements of these two to have conflicts.
Hence why they are run separately and communicate with the main handler with sockets.

