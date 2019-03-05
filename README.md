Frameworks/services/modules
Flask REST
Postgres
sqlalchemy 
alembic 



RUN LOCALLY
with Docker
docker build -t slidegraph .
docker run -t --env-file=secret.txt -p 8000:8000 slidegraph

Without Docker
source ./secret.py
gunicorn [--reload] slideshare:app


TODO
- add "secure" option to auth cookie (need ssl cert)
- move aws credentials to directory
- update affiliations
- update password
