import boto3
from botocore.config import Config


config = Config(retries={"max_attempts": 10, "mode": "standard"})
cloudfront = boto3.client("cloudfront", config=config)


def lambda_handler(event, context):
    payload = event["Payload"]
    staging_distribution_id = payload["StagingDistributionId"]
    staging_distribution_etag = cloudfront.get_distribution_config(
        Id=staging_distribution_id
    )["ETag"]

    cloudfront.delete_distribution(
        Id=staging_distribution_id, IfMatch=staging_distribution_etag
    )

    return {"Payload": payload}
