FROM python:3.10.4-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

# Set work directory
WORKDIR /code
# Copy  dependencies file
COPY ./requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependency file in this case, requirements.txt inside the /code dir
RUN pip install -r requirements.txt

# Copy project
COPY . .
