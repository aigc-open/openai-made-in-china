FROM python:3.9-buster

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . /workspace

WORKDIR /workspace

CMD "uvicorn config_plus.asgi:application --workers 10"
