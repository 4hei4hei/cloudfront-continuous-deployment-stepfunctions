import boto3
from botocore.config import Config


config = Config(retries={"max_attempts": 10, "mode": "standard"})
cloudfront = boto3.client("cloudfront", config=config)


def lambda_handler(event, context):
    payload = event["Payload"]
    primary_distribution_id = payload["PrimaryDistributionId"]
    staging_distribution_id = payload["StagingDistributionId"]

    primary_distribution_etag = cloudfront.get_distribution_config(
        Id=primary_distribution_id
    )["ETag"]
    staging_distribution_etag = cloudfront.get_distribution_config(
        Id=staging_distribution_id
    )["ETag"]

    # Staging distribution の設定を Primary distribution として昇格させる
    cloudfront.update_distribution_with_staging_config(
        Id=primary_distribution_id,
        StagingDistributionId=staging_distribution_id,
        IfMatch=f"{primary_distribution_etag}, {staging_distribution_etag}",
    )

    return {"Payload": payload}
