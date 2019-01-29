#!/bin/sh

source secret.sh
export PRODUCTION=0
export FLASK_APP=slideshare
export FLASK_ENV=production
export DB_NAME=slideshare
export DB_USER=csr2131
export DB_HOST=slideshare-prod.cshgvdefxewm.us-east-1.rds.amazonaws.com
export DB_URI_PRODUCTION=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}
export DB_URI_LOCAL=postgresql://carloruiz@localhost:5432/slideshare

if [ $PRODUCTION -eq 0 ]
then
	export DB_URI=$DB_URI_LOCAL
else
	export DB_URI=$DB_URI_PRODUCTION
fi

