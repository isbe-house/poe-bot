FROM python:3.9

WORKDIR /usr/src/app

COPY ./discord_bot/requirements.txt ./
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm requirements.txt
