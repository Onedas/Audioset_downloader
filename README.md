# Audioset downloader

---
This repository is created to make it easy to download **Audioset**.

## Pre-requisites
 - Python3

## How to start

### 1. Installation

#### - 1.1 Clone this repo:
```commandline
git clone https://github.com/Onedas/.git
```

#### - 1.2 Install ffmpeg, youtube-dl

- For conda users, you can create a new Conda environment and install, using 
    
```commandline
conda env create -f environment.yml
```
or
```commandline
```

### 2. How to Use
- All data download
it maybe takes few days(2 or 3 days)
```commandline
python downloader.py 
```

- Optional
```commandline
python downloader.py --meata [balanced_train_segments.csv | eval_segments.csv | unbalanced_train_segments.csv] 
```
