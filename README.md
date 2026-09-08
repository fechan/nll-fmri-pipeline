# NLL fMRI analysis container & scripts

## Container usage
The Docker container installs Connectome Workbench, FSL, FreeSurfer, and uv. These instructions assume you configured Docker for [rootless mode](https://docs.docker.com/engine/security/rootless/).

### First run
1. Create a folder named `workdir` in the in the repo's root directory. This is intended for your study's data, and will be mounted to the Docker container at `/workdir`.
    - Since it is separate from the Docker image, you can upgrade or remove the Docker container without affecting the workdir.
2. Copy your FreeSurfer `license.txt` to `/workdir/license.txt`.
3. Configure GPU (or lack thereof):
    - If you use an NVIDIA GPU, install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) on your machine.
    - Otherwise, remove the `deploy` section from `compose.yaml`.
4. Run `docker compose build` to build the container. Go have a nice meal― this step takes a while, because it downloads and installs very large fMRI software.
5. Run `start.sh` to start the container.

### Subsequent runs
After building the container during first time run, you can simply start the already-built container.

1. Run `start.sh`.

## Preprocessing
Preprocessing should be done with fMRIPrep (preferably on Flywheel) before running the analysis scripts on the resulting files in the Docker container.

Following these preprocessing steps will produce a BIDS compatible file structure for the raw and preprocessed data that the scripts in this repository expect. The following instructions describe how to do this on UW CHN's instance of Flywheel for a single MRI session.

### 1. BIDS curation
First, run BIDS curation so that the raw data is in a BIDS compatible file structure. This is needed for fMRIPrep to run.

1. Open your project in Flywheel, and click the `Sessions` tab to open the list of sessions.
2. Select the session you want to preprocess
3. Click `Run Gear > Analysis Gear`
4. Select `BIDS Curation` with version `2.1.3_1.0.2` (or whichever version you are using for the study.)
5. In the `Inputs` tab, under `Select Inputs`, set `template` to `chn-reproin-extension-project-template.json`. (This was provided by the CHN; for the DeafMEG project, this is in the root directory in Flywheel.)
6. In the `Configuration` tab, set `intendedfor_regexes` to `fmap-.* .*_bold`.
7. Click `Run Gear`.
8. There will be a new `curate-bids` analysis in the session's `Analyses` tab.
    * If it completes successfully, it will appear with a green checkmark. You can then see the raw data in BIDS view using the three dots menu next to `View in Launcher` and clicking `BIDS View`.
    * It if fails, then click on the analysis and see `Gear Logs` for more info. The most common failure mode is when there's a false start that hasn't been igored. In this case, find the acquisition label for the false start (e.g. `func-bold_task-langLocal_run-01`) and add rename it by appending `_ignore-BIDS` at the end (e.g. `func-bold_task-langLocal_run-01_ignore-BIDS`).

### 2. fMRIPrep
After running BIDS curation on a session, you can run fMRIPrep.

1. Click `Run Gear > Analysis Gear`
1. Select `BIDS fMRIPrep` with version `1.5.5_23.2.1` (or whichever version you are using for the study.)
1. In the `Inputs` tab, under `Select Inputs` to the following files in the project root:
    * Set `bids-filter-file` to `bids_filter_file.json` (provided by CHN)
    * Set `bidsignore` to `bidsignore.txt` (provided by CHN)
    * Set `freesurfer_license_file` to `license.txt`
1. In the `Gear Configuration` tab, set `bids_app_command` to `--output-spaces T1w MNI152NLin2009cAsym fsnative fsaverage`.
1. Click `Run Gear`.
1. Wait several hours for fMRIprep to complete.
1. If successful, you can now click on the `bids-fmriprep` analysis, and download the zip file starting with `bids-fmriprep_ses-`.

### 3. File structure for first-level analysis
1. Make a project folder in `workdir` if you haven't already (e.g. `workdir/deafmeg`).
1. The `bids-fmriprep` zip file contains a single folder with a long hexidecimal name. Extract the contents of this folder into the project folder.
    - If done correctly, your project folder should contain a `sourcedata` and a folder for your subject starting with `sub-`.
1. In `sourcedata`, create a `timing` folder. The timing data from Psychopy is not included in the fMRIPrep outputs, and this is where the timings will go for all subjects.
1. Put all your timing XLSX spreadsheets in the `timing` folder and rename them to the format `sub-<subject>_ses-<session>_run-<run>.xlsx` (e.g. `sub-DMEGp01_ses-01_run-01.xlsx`)

## Script usage
Scripts should be run inside the container, and are mounted to the `/scripts` directory in the container.

1. Run `cd /scripts`.
2. Run `uv run <the_script_you_want_to_run.py>`.
    - Tip: Adding the `--help` flag at the end (e.g. `uv run firstlevel.py --help`) describes the parameters needed for running the script.

UV will automatically download and install the dependencies in `/scripts/pyproject.toml`, and run the desired script.

### Timing file generation (`gen_timing_files.py`)
This converts XLSX timing spreadsheets in `<project_dir>/sourcedata/timing` into timing `txt` files needed by Freesurfer in `<project_dir>/derivatives/timing`.

### First-level analysis (`firstlevel.py`)
This performs first-level analysis on a single functional run with Freesurfer.

### First-level visualization (`visualize.py`)

## Basic concepts for new RAs
