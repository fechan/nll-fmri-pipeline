from typing import Optional

from nilearn.datasets import load_fsaverage_data, load_fsaverage

from surfplot import Plot
from surfplot.utils import threshold
import nibabel as nib
import numpy as np
import os
import os.path as path
from bids_path_utils import BIDSPaths
from fsl.data import featanalysis
from statistics import NormalDist
import argparse
import bids_file_finder as bff
import matplotlib.pyplot as plt

# Load fsaverage surface (reused for every visualization)
surfaces = load_fsaverage(mesh='fsaverage')
lh = surfaces['inflated'].parts['left'].file_path
rh = surfaces['inflated'].parts['right'].file_path

# Compute gyri/sulci to use as a background (reused for every visualization)
curv_sign = load_fsaverage_data(mesh='fsaverage', data_type="curvature")
for hemi, data in curv_sign.data.parts.items():
    curv_sign.data.parts[hemi] = np.sign(data)

def load_and_do_thresholding(stats_path: str, thresh: float):
    stats = nib.load(stats_path)
    return threshold(stats.darrays[0].data, thresh, two_sided=False)

def visualize_zstat(
    left_hemi_stats_path: str,
    right_hemi_stats_path: str,
    p_value: float = 0.01,
    figure_title: Optional[str] = None,
    output_path: Optional[str] = None
):
    # load and threshold data
    min_z_score = NormalDist().inv_cdf((2 - p_value) / 2.)
    stats = {
        'left': load_and_do_thresholding(left_hemi_stats_path, min_z_score),
        'right': load_and_do_thresholding(right_hemi_stats_path, min_z_score)
    }

    # make figure
    p = Plot(lh, rh)

    p.add_layer(
        {
            'left': curv_sign.data.parts['left'],
            'right': curv_sign.data.parts['right'],
        },
        cmap='gray',
        cbar=False,
        alpha=0.25,
    )
    p.add_layer(stats, cmap='hot', cbar_label='z-score')

    fig = p.build()
    if figure_title:
        fig.suptitle(figure_title)

    if output_path:
        fig.savefig(output_path)

    plt.close()

    return fig

def get_contrasts(design_file_path: str) -> dict[int, str]:
    contrasts = {}

    design = featanalysis.loadFsf(design_file_path)
    n_contrasts = int(design['ncon_real'])
    
    for contrast_number in range(1, n_contrasts + 1):
        contrasts[contrast_number] = design[f'conname_real.{contrast_number}']

    return contrasts

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='visualize',
        description='Visualize results of first-level analysis. Visualizations will appear in <project_root>/derivatives/visualization.'
    )
    parser.add_argument('project_root', help='Path to the BIDS project root (e.g. /workdir/deafmeg)')
    parser.add_argument('-p', '--p_value', type=float, default=0.01, help='P-value significance level (e.g. 0.01).')
    args = parser.parse_args()

    p_value = args.p_value

    runs = bff.list_analyzable_runs(args.project_root)
    for _, run_metadata in runs.iterrows():
        subject = run_metadata['sub']
        session = int(run_metadata['ses'])
        run = int(run_metadata['run'])

        bids = BIDSPaths(args.project_root, subject, session, run)
        viz_dir = path.join(bids.derivatives(), 'visualization')
        os.makedirs(viz_dir, exist_ok=True)

        contrasts = get_contrasts(bids.prepared_firstlevel_design_file())
        for contrast_number, contrast_name in contrasts.items():
            stats_fname = f'zstat{contrast_number}.func.gii'
            visualize_zstat(
                left_hemi_stats_path=path.join(bids.stats_surface_fsl(hemisphere='L'), stats_fname),
                right_hemi_stats_path=path.join(bids.stats_surface_fsl(hemisphere='R'), stats_fname),
                p_value=p_value,
                figure_title=f'{contrast_name}, {subject} session {session} run {run} (p <= {p_value})',
                output_path=path.join(viz_dir, f'sub-{subject}_ses-{session}_run-{run}_desc-zstat{contrast_number}.png')
            )