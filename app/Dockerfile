# pull official base image
FROM python:3.8.5-slim-buster

# set work directory
ENV APP_HOME=/usr/src/app
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat build-essential python3-dev python3-pip \ 
    python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \ 
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# install dependencies
RUN pip install --upgrade pip
RUN python -m pip install --upgrade setuptools
COPY requirements requirements
RUN pip install -r requirements/dev.txt

# create the appropriate directories
RUN mkdir static

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]