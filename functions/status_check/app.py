import boto3


cloudfront = boto3.client("cloudfront")


def lambda_handler(event, context):
    payload = event["Payload"]
    primary_distribution_id = payload["PrimaryDistributionId"]
    staging_distribution_id = payload["StagingDistributionId"]

    # Primary / Staging distribution の状態を取得して利用可能かを判定させる
    primary_distribution_status_result = cloudfront.get_distribution(
        Id=primary_distribution_id
    )["Distribution"]["Status"]
    staging_distribution_status_result = cloudfront.get_distribution(
        Id=staging_distribution_id
    )["Distribution"]["Status"]

    return {
        "Payload": payload
        | {
            "PrimaryDistributionStatusResult": primary_distribution_status_result,
            "StagingDistributionStatusResult": staging_distribution_status_result,
        }
    }
