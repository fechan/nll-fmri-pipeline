# NLL fMRI analysis container & scripts

## Container usage
The Docker container installs Connectome Workbench, FSL, FreeSurfer, and uv. These instructions assume you configured Docker for [rootless mode](https://docs.docker.com/engine/security/rootless/).

### First run
1. Create a folder named `workdir` in the in the repo's root directory. This is intended for your study's data, and will be mounted to the Docker container at `/workdir`.
2. Copy your FSL `license.txt` to `/workdir/license.txt`.
3. Configure GPU (or lack thereof):
  - If you use an NVIDIA GPU, install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) on your machine.
  - Otherwise, remove the `deploy` section from `compose.yaml`.
4. Run `docker compose build` to build the container. This will take a while, as it will download and install very large fMRI software.
5. Run `start.sh` to start the container.

### Subsequent runs
After building the container during first time run, you can simply start the already-built container.

1. Run `start.sh`.

## Script usage
Scripts should be run inside the container, and are mounted to the `/scripts` directory in the container.

1. Run `cd /scripts`.
2. Run `uv run <the_script_you_want_to_run.py>`.

UV will automatically download and install the dependencies in `/scripts/pyproject.toml`, and run the desired script.