#!/bin/bash

list=`aws ssm get-parameter --name slidegraph-production-secrets --region us-east-1 --with-decryption --query Parameter.Value --output text`

while read -r var; do
	export "$var"
done <<< "$list"

exec gunicorn --bind=0.0.0.0:80 -w 3 -k aiohttp.worker.GunicornWebWorker slideshare:aioapp
