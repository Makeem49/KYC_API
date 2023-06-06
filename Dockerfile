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

ENV DJANGO_SECRET_KEY your_secret_key_here
ENV POSTGRES_USER eky_db_admin
ENV POSTGRES_PASSWORD eky_db_admin_password
ENV POSTGRES_DB eky_db
ENV DJANGO_SECRET_KEY ^tctt1^lox*fdu+t&*fjshua 
ENV DJANGO_DEBUG True 
ENV SQL_ENGINE django.db.backends.postgresql 
ENV SQL_DATABASE eky_db 
ENV SQL_USER eky_db_admin 
ENV SQL_PASSWORD eky_db_admin_password 
ENV SQL_HOST db 
ENV SQL_PORT 5432 


