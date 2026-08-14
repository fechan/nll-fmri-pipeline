from typing import Optional

from neuromaps.datasets import fetch_fsaverage
from surfplot import Plot
from surfplot.utils import threshold
import nibabel as nib
import os
import os.path as path
from bids_path_utils import BIDSPaths
from fsl.data import featanalysis
from statistics import NormalDist

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
    surfaces = fetch_fsaverage(density='164k')
    lh, rh = surfaces['inflated']

    min_z_score = NormalDist().inv_cdf((2 - p_value) / 2.)
    stats = {
        'left': load_and_do_thresholding(left_hemi_stats_path, min_z_score),
        'right': load_and_do_thresholding(right_hemi_stats_path, min_z_score)
    }

    # make figure
    p = Plot(lh, rh)
    p.add_layer(stats, cmap='hot')

    fig = p.build()
    if figure_title:
        fig.suptitle(figure_title)

    if output_path:
        fig.savefig(output_path)

    return fig

def get_contrast_name(design_file_path: str, contrast_number: int):
    design = featanalysis.loadFsf(design_file_path)
    contrast_name = design[f'conname_real.{contrast_number}']
    return contrast_name

def get_number_of_contrasts(design_file_path: str):
    design = featanalysis.loadFsf(design_file_path)
    contrasts = design['ncon_real']
    return int(contrasts)

if __name__ == '__main__':
    p_value = 0.01
    subject = 'DMEGp01'
    session = 1
    run = 1

    bids = BIDSPaths('/workdir/deafmeg', subject, session, run)
    contrasts = get_number_of_contrasts(bids.prepared_firstlevel_design_file())

    for contrast_number in range(1, contrasts + 1):
        contrast_name = get_contrast_name(bids.prepared_firstlevel_design_file(), contrast_number)

        viz_dir = path.join(bids.derivatives(), 'visualization')
        os.makedirs(viz_dir, exist_ok=True)

        stats_fname = f'zstat{contrast_number}.func.gii'
        visualize_zstat(
            left_hemi_stats_path=path.join(bids.stats_surface_fsl(hemisphere='L'), stats_fname),
            right_hemi_stats_path=path.join(bids.stats_surface_fsl(hemisphere='R'), stats_fname),
            p_value=p_value,
            figure_title=f'{contrast_name}, {subject} session {session} run {run} (p <= {p_value})',
            output_path=path.join(viz_dir, f'sub-{subject}_ses-{session}_run-{run}_desc-zstat{contrast_number}.png')
        )