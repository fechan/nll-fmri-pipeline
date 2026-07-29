from typing import Optional

from fsl.data import featanalysis
import os.path as path
import argparse
import pandas as pd

import logging
logger = logging.getLogger(__name__)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def prepare_fsl_confound_file(
    confounds_tsv_path: str, # Path to confounds TSV
    confound_ev_cols: list[str], # Confound EV columns to use
    output_confounds_path: str, # Path to output confounds file
    demean: bool = True # Whether to subtract the mean from each confound variable
):
    confounds_tsv = pd.read_csv(confounds_tsv_path, sep='\t')
    confounds_tsv = confounds_tsv[confound_ev_cols]

    if demean:
        confounds_tsv = confounds_tsv - confounds_tsv.mean()

    confounds_tsv = confounds_tsv.fillna(0)

    confounds_tsv.to_csv(
        output_confounds_path,
        sep='\t',
        index=False,
        header=False,
    )

def prepare_design(
    template_fsf_path: str, # Input template design
    prepared_fsf_path: str, # Output prepared design
    input_4d_data_path: str, # 4d brain data to run FEAT on
    firstlevel_outputs_path: str, # Directory where FEAT will dump analysis files to
    ev_paths: list[str], # EV/timing file in 3 column format
    confounds_path: Optional[str] = None, # Confounds file for FSL
    tr: float = 2,
    hpf: float = 128,
):
    '''Modify the template design FSF to be used with the given functional MRI
    data, and save the modified design to the output path.'''
    logger.info('Preparing design')
    design = featanalysis.loadFsf(template_fsf_path)

    design['outputdir'] = firstlevel_outputs_path
    design['tr'] = tr
    design['paradigm_hp'] = hpf
    design['inputtype'] = 2
    if confounds_path:
        design['confoundevs'] = 1
    if 'npts' in design:
        del design['npts'] # allow FEAT to infer the total volumes from the input file

    # regular EVs
    for ev_number, ev_path in enumerate(ev_paths, 1):
        if f'custom{ev_number}' not in design:
            raise ValueError('Too many explanatory variables (EVs) passed in for the given design template! If you need to add more EVs, you should load your design in FEAT and add all your variables first, then re-save the template.')
        
        evtitle = design[f'evtitle{ev_number}']
        logger.info(f'EV {evtitle}: using file {ev_path}')
        design[f'custom{ev_number}'] = ev_path

    logger.info('Writing design file')
    with open(prepared_fsf_path, 'w') as out_fsf:
        out_fsf.write(f'# This design was automatically generated from {template_fsf_path} using firstlevel.py\n\n')

        if 'feat_files' in design:
            del design['feat_files']
        out_fsf.write(f'set feat_files(1) "{input_4d_data_path}"\n')

        if 'confoundev_files' in design:
            del design['confoundev_files']
        if confounds_path:
            out_fsf.write(f'set confoundev_files(1) "{confounds_path}"\n')

        for setting, value in design.items():
            if not is_number(value):
                out_fsf.write(f'set fmri({setting}) "{value}"\n')  
            else:
                out_fsf.write(f'set fmri({setting}) {value}\n')  

if __name__ == "__main__":
    logging.basicConfig(filename='logs/firstlevel.log', level=logging.INFO)

    fsl_confounds_path = '/workdir/deafmeg/derivatives/fsl-scripted/sub-DMEGp01_ses-01_task-langLocal_run-01_confounds.txt'
    prepare_fsl_confound_file(
        confounds_tsv_path='/workdir/deafmeg/sub-DMEGp01/ses-01/func/sub-DMEGp01_ses-01_task-langLocal_run-01_desc-confounds_timeseries.tsv',
        confound_ev_cols=['rmsd', 'white_matter'],
        output_confounds_path=fsl_confounds_path,
        demean=True
    )

    prepare_design(
        template_fsf_path='/workdir/deafmeg/derivatives/fsl/firstlevel_4cond.fsf',
        prepared_fsf_path='/workdir/deafmeg/derivatives/fsl-scripted/sub-DMEGp01_ses-01_task-langLocal_run-01_firstlevel.fsf',
        input_4d_data_path='/workdir/deafmeg/sub-DMEGp01/ses-01/func/sub-DMEGp01_ses-01_task-langLocal_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold',
        ev_paths=[
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-Action.txt',
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-ASL.txt',
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-Control.txt',
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-Silly.txt',
        ],
        confounds_path=fsl_confounds_path,
        firstlevel_outputs_path='/workdir/deafmeg/derivatives/fsl/sub-DMEGp01/ses-01'
    )
