#!/bin/bash

list=`aws ssm get-parameter --name slidegraph-production-secrets --region us-east-1 --with-decryption --query Parameter.Value --output text`

if [ -z "$list" ]
then
	>&2 echo "AWS credentials not set"
	exit 1
else
	echo "AWS credentials loaded properly"
fi

while read -r var; do
	export "$var"
done <<< "$list"

exec gunicorn --bind=0.0.0.0:80 -w 3 -k aiohttp.worker.GunicornWebWorker slideshare:aioapp
