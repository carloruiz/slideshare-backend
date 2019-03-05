Frameworks/services/modules
Flask REST
Postgres
sqlalchemy 
alembic 


secret file format
DB_PASSWORD=[]
SECRET_KEY=[]
AWS_SECRET_ACCESS_KEY=[]
AWS_ACCESS_KEY_ID=[]

Updating base docker image (libreoffice-base) in DockerHub
docker build --target libreoffice-base -t libreoffice-base .
docker push csr2131/libreoffice-base

RUN LOCALLY
with Docker
docker build -t slidegraph .
docker run -t --env-file=secret.env -p 8000:8000 slidegraph

Without Docker
source ./secret.sh
gunicorn [--reload] slideshare:app


TODO
- add "secure" option to auth cookie (need ssl cert)
- move aws credentials to directory
- update affiliations
- update password
