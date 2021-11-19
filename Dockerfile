FROM ubuntu:18.04

WORKDIR /opt
COPY . /opt

USER root

RUN apt-get update
RUN apt-get install -y wget \
                       gdal-bin \
                       libgdal-dev \
                       libspatialindex-dev \
                       build-essential \
                       software-properties-common \
                       apt-utils \
                       ffmpeg \
                       libsm6 \
                       libxext6 \
                       libtcmalloc-minimal4
RUN wget https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz
RUN tar -xzf Python-3.9.5.tgz
RUN cd Python-3.9.5/ && ./configure --with-ensurepip=install && make && make install
RUN export export LD_PRELOAD="/usr/lib/libtcmalloc_minimal.so.4"
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update
RUN apt-get install -y libgdal-dev
# RUN pip3 install --upgrade pip
RUN /usr/local/bin/python3.9 -m pip install -r requirements.txt
RUN python3.9 -m pip install https://storage.googleapis.com/open3d-releases-master/python-wheels/open3d-0.13.0+454e1ce-cp39-cp39-manylinux_2_27_x86_64.whl
RUN wget http://download.osgeo.org/libspatialindex/spatialindex-src-1.7.1.tar.gz
RUN tar -xvf spatialindex-src-1.7.1.tar.gz
RUN cd spatialindex-src-1.7.1/ && ./configure && make && make install
RUN ldconfig
RUN add-apt-repository ppa:ubuntugis/ppa
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

ENTRYPOINT [ "/usr/bin/python3", "/opt/Remove_extra_plants_from_pointcloud.py" ]