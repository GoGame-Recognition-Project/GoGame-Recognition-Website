FROM python:3.9.13-slim-buster

WORKDIR /usr/app/src

COPY . .

ADD requirements.txt .

RUN pip install --upgrade pip

RUN python -m pip install -r requirements.txt

RUN pip3 install opencv-python-headless==4.5.3.56

CMD [ "python", "./run.py"]