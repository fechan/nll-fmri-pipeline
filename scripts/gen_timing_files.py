import pandas as pd
import os
import os.path as path
import numpy as np
import argparse
import bids_file_finder as bff

def generate_3column(
    timing_spreadsheet_meta: pd.Series, # Series with metadata about the timing spreadsheet file
    derivatives_timing_root: str, # Directory in derivatives that all the newly generated timing txt files should go
    conditions: list[str] = ["Action","ASL","Control","Silly"],
):
    subject_id = timing_spreadsheet_meta['sub']
    session_id = timing_spreadsheet_meta['ses']
    run_id = timing_spreadsheet_meta['run']

    data_file_path = timing_spreadsheet_meta['path']
    output_dir = path.join(
        derivatives_timing_root,
        f'sub-{subject_id}',
        f'ses-{session_id}'
    )
    os.makedirs(output_dir, exist_ok=True)

    # Load the XLSX, select only relevant columns, and preprocess them
    run_data_df = pd.read_excel(data_file_path)

    short_df = run_data_df[["Condition","Verb","trial_onset", "trial_dur"]]
    short_df["trial_onset"] = round(short_df["trial_onset"],1)
    short_df["trial_dur"] = round(short_df["trial_dur"],1)
    short_df["regressor_height"] = 1

    # Save rest and break conditions as one rest timing TXT
    rest_df = short_df[(short_df["Condition"]=="Rest") | (short_df["Condition"]=="Break")]
    rest_output_path = path.join(output_dir, f"sub-{subject_id}_ses-{session_id}_run-{run_id}_desc-timingRest.txt")
    np.savetxt(rest_output_path, rest_df[["trial_onset", "trial_dur","regressor_height"]].values, fmt=['%1.1f','%1.1f','%d'])

    # Save timing TXTs for the other conditions
    for condition in conditions:
        condition_df = short_df[short_df["Condition"]==condition]
        condition_output_path = path.join(output_dir, f"sub-{subject_id}_ses-{session_id}_run-{run_id}_desc-timing{condition}.txt")
        np.savetxt(condition_output_path, condition_df[["trial_onset", "trial_dur","regressor_height"]].values, fmt=['%1.1f','%1.1f','%d'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='gen_timing_files',
        description='Generate FSL 3-column timing files from XLSX spreadsheets',
    )
    parser.add_argument('timing_dir', help='Root path of the timing files (e.g. /workdir/deafmeg/sourcedata/timing).')
    args = parser.parse_args()

    files_in = bff.list_files(args.timing_dir)
    files_in = files_in[files_in.extension == '.xlsx']

    for _, file_meta in files_in.iterrows():
        generate_3column(
            timing_spreadsheet_meta=file_meta,
            derivatives_timing_root='/workdir/deafmeg/derivatives/timing'
        )
