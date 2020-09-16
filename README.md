# TissueVision Technical Questions

This README provides setup and logistical information about code written for the TissueVision Technical Interview questions.

## Installation

Technical code for these questions is written in Python.
All necessary packages and dependencies to run this code have been listed: 
For `pip` users: `~/requirements.txt`  
* Load packages via `pip install -r requirements.txt`

For `conda` users: `~/tvi.yml`
* Load "tvi" environment via `conda env create -f tvi.yml`

## File Organization and Running Code

To generate results for all programmatic questions, please run `main.py`. 
`main.py` displays the extracted metadata for TQ1 and the segmentation metric in TQ2 to `stdout`. 
A copy of sample output is provided in `~/output/stdout.txt`.

`main.py` utilizes several modular functions contained within the `tvi_knesis` package.
These functions are collected within `~/tvi_knesis/` and include:
* `extract_tif_meta.py` - [TQ1]
* `segment_mask.py`		- [TQ2]
* `jaccard.py`			- [TQ3]
* `sdnr.py`				- [TQ4]

`~/data/` contains the data provided by TVI for these questions. The directory structure has not been changed. 

`~/output/` contains a complete copy of all output files created with main.py.
These files include:
* `segmask_41077_120219_S000090.tif` - [TQ2 Segmentation Mask]
* `regions_41077_120219_S000090.csv` - [TQ3 ROI Feature Table]
* `sdnr_41077_120219.png` - [TQ4 Signal Difference Series Plot]
* `stdout.txt` - [Runtime print statements (TQ1/TQ2 Output)]
 
Technical comments and answers to written questions are provided in `~/ANSWERS.md`.


