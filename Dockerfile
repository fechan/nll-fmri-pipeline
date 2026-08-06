FROM ubuntu:20.04

# Install FSL and UV

ENV FSLDIR          "/usr/local/fsl"
ENV DEBIAN_FRONTEND "noninteractive"
ENV LANG            "en_GB.UTF-8"

RUN apt-get update  -y && \
    apt-get upgrade -y && \
    apt-get install -y    \
      python          \
      wget            \
      file            \
      dc              \
      mesa-utils      \
      pulseaudio      \
      libquadmath0    \
      libgtk2.0-0     \
      firefox         \
      libgomp1        \
      python3-pip     \
      unzip           \
      libopengl0      \
      x11-apps          && \
    pip install uv

RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py && \
    python ./fslinstaller.py -d /usr/local/fsl/ && \
    rm fslinstaller.py

# Install Connectome Workbench

RUN wget https://humanconnectome.org/storage/app/media/workbench/workbench-linux64-v2.2.1.zip -O workbench.zip && \
    unzip workbench.zip -d /opt && \
    rm workbench.zip
ENV PATH="$PATH:/opt/workbench/bin_linux64"

# Install FreeSurfer

RUN apt-get -y install gdebi-core
RUN wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/8.1.0/freesurfer_ubuntu20-8.1.0_amd64.deb -O freesurfer.deb && \
    sh -c 'yes | gdebi freesurfer.deb' && \
    rm freesurfer.deb

ENV USER "root"
ENTRYPOINT [ "sh", "-c", ". /usr/local/fsl/etc/fslconf/fsl.sh && /bin/bash" ]