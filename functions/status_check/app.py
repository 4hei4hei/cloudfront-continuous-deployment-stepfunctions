import boto3
from botocore.config import Config


config = Config(retries={"max_attempts": 10, "mode": "standard"})
cloudfront = boto3.client("cloudfront", config=config)


def lambda_handler(event, context):
    payload = event["Payload"]
    primary_distribution_id = payload["PrimaryDistributionId"]
    staging_distribution_id = payload["StagingDistributionId"]
    distribution_status_result = "ng"

    # Distribution の状態を取得して利用可能かを判定させる
    primary_distribution_status_result = cloudfront.get_distribution(
        Id=primary_distribution_id
    )["Distribution"]["Status"]
    staging_distribution_status_result = cloudfront.get_distribution(
        Id=staging_distribution_id
    )["Distribution"]["Status"]

    if (
        primary_distribution_status_result == "Deployed"
        and staging_distribution_status_result == "Deployed"
    ):
        distribution_status_result = "ok"
        primary_distribution_etag = cloudfront.get_distribution_config(
            Id=primary_distribution_id
        )["ETag"]
        staging_distribution_etag = cloudfront.get_distribution_config(
            Id=staging_distribution_id
        )["ETag"]
        return {
            "Payload": payload
            | {
                "DistributionStatusResult": distribution_status_result,
                "PrimaryDistributionETag": primary_distribution_etag,
                "StagingDistributionETag": staging_distribution_etag,
            }
        }
    else:
        distribution_status_result = "ng"
        return {
            "Payload": payload
            | {"DistributionStatusResult": distribution_status_result}
        }
