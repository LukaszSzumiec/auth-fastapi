FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
ENV PYTHONUNBUFFERED=1
RUN mkdir /src
WORKDIR /src
COPY requirements.txt /src/
# RUN pip3 install pipenv
RUN pip3 install -r requirements.txt
COPY . /src/