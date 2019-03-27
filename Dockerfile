FROM csr2131/libreoffice-base

RUN apt-get -y -q install python3-pip python3-venv git awscli poppler-utils
ARG DEPENDENCYCACHE
RUN git clone https://github.com/carloruiz/slideshare-backend.git \
	&& cd slideshare-backend \
	&& pip3 install -r requirements.txt 

WORKDIR slideshare-backend
ARG CODECASH 
RUN git pull
EXPOSE 80
EXPOSE 443
VOLUME ["/tmp"]

#for development, uncomment the next three lines, and comment out the last one. 
#RUN mkdir slideshare-backend-local
#WORKDIR slideshare-backend-local
#CMD ["gunicorn", "--bind=0.0.0.0:8000", "--reload", "slideshare:app"]

CMD ["gunicorn", "--bind=0.0.0.0:80", "-w", "3", "-k", "aiohttp.worker.GunicornWebWorker", "slideshare:aioapp"]
#ENTRYPOINT ["./runserver.sh"]

