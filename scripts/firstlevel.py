from fsl.data import featanalysis
import argparse

import logging
logger = logging.getLogger(__name__)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def prepare_design(
    template_fsf_path: str, # Input template design
    prepared_fsf_path: str, # Output preared design
    input_4d_data_path: str, # 4d brain data to run FEAT on
    firstlevel_outputs_path: str, # Directory where FEAT will dump analysis files to
    ev_paths: list[str], # EV/timing file in 3 column format
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
    if 'npts' in design:
        del design['npts'] # allow FEAT to infer the total volumes from the input file

    # regular EVs
    for ev_number, ev_path in enumerate(ev_paths, 1):
        if f'custom{ev_number}' not in design:
            raise ValueError('Too many explanatory variables (EVs) passed in for the given design template! If you need to add more EVs, you should load your design in FEAT and add all your variables first, the re-save the template.')
        
        evtitle = design[f'evtitle{ev_number}']
        logger.info(f'EV {evtitle}: using file {ev_path}')
        design[f'custom{ev_number}'] = ev_path


    # confound EVs
    # TODO: implement me

    logger.info('Writing design file')
    with open(prepared_fsf_path, 'w') as out_fsf:
        out_fsf.write(f'# This design was automatically generated from {template_fsf_path} using firstlevel.py\n\n')

        if 'feat_files' in design:
            del design['feat_files']
        out_fsf.write(f'set feat_files(1) "{input_4d_data_path}"\n')

        for setting, value in design.items():
            if not is_number(value):
                out_fsf.write(f'set fmri({setting}) "{value}"\n')  
            else:
                out_fsf.write(f'set fmri({setting}) {value}\n')  

if __name__ == "__main__":
    logging.basicConfig(filename='logs/firstlevel.log', level=logging.INFO)

    prepare_design(
        template_fsf_path='../workdir/deafmeg/derivatives/fsl/firstlevel_4cond.fsf',
        prepared_fsf_path='../workdir/deafmeg/derivatives/fsl-scripted/sub-DMEGp01_ses-01_task-langLocal_run-01_firstlevel.fsf',
        input_4d_data_path='/workdir/deafmeg/sub-DMEGp01/ses-01/func/sub-DMEGp01_ses-01_task-langLocal_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold',
        ev_paths=[
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-Action.txt',
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-ASL.txt',
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-Control.txt',
            '/workdir/deafmeg/derivatives/timing/sub-DMEGp01/ses-01/ASLAct_01-Silly.txt',
        ],
        firstlevel_outputs_path='/workdir/deafmeg/derivatives/fsl/sub-DMEGp01/ses-01'
    )
