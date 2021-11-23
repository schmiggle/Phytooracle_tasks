FROM ubuntu:18.04

WORKDIR /opt
COPY . /opt

USER root

RUN apt-get update
RUN apt-get install -y wget \
                       build-essential \
                       software-properties-common \
                       apt-utils \
                       libgl1-mesa-glx \
                       ffmpeg \
                       libsm6 \
                       libxext6 \
                       libffi-dev \
                       libbz2-dev \
                       zlib1g-dev \
                       libreadline-gplv2-dev \
                       libncursesw5-dev \
                       libssl-dev \
                       libsqlite3-dev \
                       tk-dev \
                       libgdbm-dev \
                       libc6-dev \
                       liblzma-dev
                       
RUN wget https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz
RUN tar -xzf Python-3.9.5.tgz
RUN cd Python-3.9.5/ && ./configure --with-ensurepip=install && make && make install

RUN apt-get update
RUN pip3 install -r requirements.txt
RUN python3.9 -m pip install https://storage.googleapis.com/open3d-releases-master/python-wheels/open3d-0.13.0+454e1ce-cp39-cp39-manylinux_2_27_x86_64.whl
RUN apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

ENTRYPOINT [ "/usr/bin/python3", "/opt/Remove_extra_plants_from_pointcloud.py" ]
