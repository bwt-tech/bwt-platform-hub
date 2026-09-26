#!/bin/bash
export AWS_ACCESS_KEY_ID=test 
export AWS_SECRET_ACCESS_KEY=test

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/reverse_scheduler/batch_size" \
    --value "1" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/reverse_scheduler/enabled" \
    --value "true" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/reverse_scheduler/cron" \
    --value "* * * * *" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/scheduler/batch_size" \
    --value "10" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/scheduler/enabled" \
    --value "true" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/scheduler/cron" \
    --value "* * * * *" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 secretsmanager put-secret-value \
    --secret-id "secrets_bwt" \
    --secret-string "{\"OCTADESK_API_KEY\":\"\",\"OCTADESK_BASE_URL\":\"\",\"OCTADESK_SUBDOMAIN\":\"\",\"RDSTATION_TOKEN\":\"\",\"SENTRY_URL\":\"\", \"BWT_EMAIL\":\"supervisor_vendas@b2bit.company\", \"BWT_PASSWORD\": \"b2bit123\", \"BWT_URL\": \"https://api.homolog.brasileiroswinetours.com.br\"}"

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/dev/database/password" \
    --value "postgrespassword" \
    --type "SecureString" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/dev/database/host" \
    --value "localhost" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/dev/database/name" \
    --value "bwt_platform" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/dev/database/port" \
    --value "5432" \
    --type "String" \
    --overwrite

aws --endpoint-url=http://localhost:4566 ssm put-parameter \
    --name "/bwt/dev/database/username" \
    --value "postgres" \
    --type "String" \
    --overwrite