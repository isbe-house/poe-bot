FROM jupyter/scipy-notebook:b94c2f2db600 AS JUPYTER

USER root

RUN apt update
RUN apt install -y vim iputils-ping

USER jovyan

RUN pip install --upgrade pip

COPY poe_lib/requirements_poe_lib.txt ./
RUN pip install -r requirements_poe_lib.txt
RUN rm requirements_poe_lib.txt
