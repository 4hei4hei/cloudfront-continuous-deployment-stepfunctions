#!/bin/bash

BUCKET_NAME=cfcd-workflow-web-local

awslocal s3 mb s3://${BUCKET_NAME}
echo 'Hello World' > /tmp/hello.txt
awslocal s3 cp /tmp/hello.txt s3://${BUCKET_NAME}/hello.txt --acl public-read
rm /tmp/hello.txt

domain=$(awslocal cloudfront create-distribution \
   --origin-domain-name ${BUCKET_NAME}.s3.amazonaws.com | jq -r '.Distribution.DomainName')
curl -k https://$domain/hello.txt

awslocal ssm put-parameter --name /cfcd-workflow/local --type String --value '{"DistributionConfig": {"DefaultRootObject": "local/index.html"}}'
