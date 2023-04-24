FROM python:3.7

FROM ubuntu:focal
RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get install -y software-properties-common && apt-get update
RUN  add-apt-repository ppa:ubuntugis/ppa &&  apt-get update
RUN apt-get install -y gdal-bin libgdal-dev
RUN apt-get install -y python3-pip
ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
ARG C_INCLUDE_PATH=/usr/include/gdal
WORKDIR /usr/src/app
COPY darcy .
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY script.sh /
RUN chmod +x /script.sh
