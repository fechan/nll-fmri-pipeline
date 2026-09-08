from glob import glob
import pandas as pd
import os.path as path

def get_metadata(bids_filename: str):
    metadata = {}

    name, extension = path.splitext(bids_filename)
    metadata['extension'] = extension

    entities = name.split('_')
    if '-' not in entities[-1]:
        metadata['suffix'] = entities[-1]
        entities = entities[:-1]

    for entity in entities:
        try:
            key, value = entity.split('-')
            metadata[key] = value
        except ValueError:
            print(f'Possibly non-BIDS compliant filename: {bids_filename}')

    return metadata

def list_files(root: str, recursive: bool = True):
    file_metadata = []

    all_paths = glob(f'{root}/**/*', recursive=recursive)
    all_files = [f for f in all_paths if path.isfile(f)]

    for fpath in all_files:
        basename = path.basename(fpath)

        file_metadata.append(dict({
            'path': fpath,
            'name': basename,
        }, **get_metadata(basename)))

    return pd.DataFrame(file_metadata)

def list_analyzable_runs(project_root: str):
    timing_dir = path.join(project_root, 'derivatives/timing')
    return list_files(timing_dir)[['sub','ses','run']].drop_duplicates()
