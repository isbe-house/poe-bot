FROM python:3.9

WORKDIR /usr/src/app

COPY ./poe_lib/requirements_poe_lib.txt ./poe_lib/
COPY ./tests/requirements_tests.txt ./tests/
RUN python -m pip install --upgrade pip
RUN pip install -r ./poe_lib/requirements_poe_lib.txt
RUN pip install -r ./tests/requirements_tests.txt
RUN rm -rf ./poe_lib/ ./tests/
