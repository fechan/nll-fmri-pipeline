FROM ubuntu:20.04

ENV FSLDIR          "/usr/local/fsl"
ENV DEBIAN_FRONTEND "noninteractive"
ENV LANG            "en_GB.UTF-8"

RUN apt update  -y && \
    apt upgrade -y && \
    apt install -y    \
      python          \
      wget            \
      file            \
      dc              \
      mesa-utils      \
      pulseaudio      \
      libquadmath0    \
      libgtk2.0-0     \
      firefox         \
      libgomp1

RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py
RUN python ./fslinstaller.py -d /usr/local/fsl/

RUN apt-get install -y python3-pip x11-apps
RUN pip install uv

ENV USER "root"
ENTRYPOINT [ "sh", "-c", ". /usr/local/fsl/etc/fslconf/fsl.sh && /bin/bash" ]