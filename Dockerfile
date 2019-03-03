FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get -y -q install gdb libreoffice libreoffice-writer ure libreoffice-java-common libreoffice-core libreoffice-common openjdk-8-jre fonts-opensymbol hyphen-fr hyphen-de hyphen-en-us hyphen-it hyphen-ru fonts-dejavu fonts-dejavu-core fonts-dejavu-extra fonts-droid-fallback fonts-dustin fonts-f500 fonts-fanwood fonts-freefont-ttf fonts-liberation fonts-lmodern fonts-lyx fonts-sil-gentium fonts-texgyre fonts-tlwg-purisa
RUN apt-get -y -q remove libreoffice-gnome
RUN adduser --home=/opt/libreoffice --disabled-password --gecos "" --shell=/bin/bash libreoffice


RUN apt-get -y -q install python3-pip git awscli poppler-utils
RUN git clone https://github.com/carloruiz/slideshare-backend.git \
	&& cd slideshare-backend \
	&& pip3 install -r requirements.txt 


WORKDIR /slideshare-backend
COPY secret.py /slideshare-backend/

EXPOSE 8000

VOLUME ["/tmp"]

ARG DUMMY=master
RUN git pull

CMD ["gunicorn", "--bind=0.0.0.0:8000", "slideshare:app"]
