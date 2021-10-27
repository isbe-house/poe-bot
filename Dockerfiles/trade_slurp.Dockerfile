FROM python:3.9

WORKDIR /usr/src/app

RUN python -m pip install --upgrade pip

COPY ./poe_lib/requirements_poe_lib.txt ./poe_lib/
RUN pip install -r ./poe_lib/requirements_poe_lib.txt
RUN rm ./poe_lib/requirements_poe_lib.txt

COPY ./trade_slurp/requirements.txt ./
RUN pip install -r requirements.txt
RUN rm requirements.txt
