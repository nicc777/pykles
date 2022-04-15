FROM ubuntu:21.04 AS node-explorer-rest

LABEL Description="A container for the production hosting of the pykles REST API" Vendor="none" Version="0.1"

# Prep Python
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y
RUN apt-get install libterm-readline-gnu-perl apt-utils -y
RUN apt-get install -y python3 python3-pip
RUN pip3 install kubernetes fastapi "uvicorn[standard]"




FROM node-explorer-rest

LABEL Description="A REST API for Kubernetes Node Resource Queries" Vendor="none" Version="0.1"

# Envieonment
ENV DEBUG "0"

# Install the app
WORKDIR /usr/src/app
RUN mkdir dist
COPY dist/*.tar.gz ./dist/
RUN pip3 install dist/*.tar.gz

# Operational Configuration
EXPOSE 8080
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--no-access-log", "pykles.pykles:app"]



