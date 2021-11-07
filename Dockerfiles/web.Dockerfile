FROM python:3.9

WORKDIR /usr/src/app

COPY web/requirements_web.txt ./
RUN python -m pip install --upgrade pip
RUN pip install -r requirements_web.txt
RUN rm requirements_web.txt

COPY ./poe_lib/requirements_poe_lib.txt ./poe_lib/
RUN pip install -r ./poe_lib/requirements_poe_lib.txt
RUN rm ./poe_lib/requirements_poe_lib.txt