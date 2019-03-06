FROM ubuntu:18.04 AS base_image
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get -y -q install gdb libreoffice libreoffice-writer ure libreoffice-java-common libreoffice-core libreoffice-common openjdk-8-jre fonts-opensymbol hyphen-fr hyphen-de hyphen-en-us hyphen-it hyphen-ru fonts-dejavu fonts-dejavu-core fonts-dejavu-extra fonts-droid-fallback fonts-dustin fonts-f500 fonts-fanwood fonts-freefont-ttf fonts-liberation fonts-lmodern fonts-lyx fonts-sil-gentium fonts-texgyre fonts-tlwg-purisa
RUN apt-get -y -q remove libreoffice-gnome
RUN adduser --home=/opt/libreoffice --disabled-password --gecos "" --shell=/bin/bash libreoffice
RUN apt-get -y -q install python3-pip python3-venv git awscli poppler-utils

# application code
FROM base_image
ARG DUMMY=master
RUN git clone https://github.com/carloruiz/slideshare-backend.git \
	&& cd slideshare-backend \
	&& pip3 install -r requirements.txt 

EXPOSE 80
EXPOSE 443
VOLUME ["/tmp"]

#for development, uncomment the next three lines, and comment out the last CMD
#RUN mkdir slideshare-backend-local
#WORKDIR slideshare-backend-local
#CMD ["gunicorn", "--bind=0.0.0.0:8000", "--reload", "slideshare:app"]

WORKDIR slideshare-backend
#CMD ["gunicorn", "--bind=0.0.0.0:80", "-w", "3", "-k", "aiohttp.worker.GunicornWebWorker", "slideshare:aioapp"]
ENTRYPOINT ["./runserver.sh"]

