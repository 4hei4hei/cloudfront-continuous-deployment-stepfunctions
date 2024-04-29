import boto3


cloudfront = boto3.client("cloudfront")


def lambda_handler(event, context):
    payload = event["Payload"]
    staging_distribution_id = payload["StagingDistributionId"]
    staging_distribution_etag = cloudfront.get_distribution_config(
        Id=staging_distribution_id
    )["ETag"]
    staging_distribution_config = cloudfront.get_distribution_config(
        Id=staging_distribution_id
    )["DistributionConfig"]

    continuous_deployment_policy_id = payload["ContinuousDeploymentPolicyId"]
    continuous_deployment_policy_etag = (
        cloudfront.get_continuous_deployment_policy_config(
            Id=continuous_deployment_policy_id
        )["ETag"]
    )

    # Continuous deployment policy を削除する
    cloudfront.delete_continuous_deployment_policy(
        Id=continuous_deployment_policy_id, IfMatch=continuous_deployment_policy_etag
    )

    # Staging distribution を Disabled にし、Continuous deployment policy の関連付けを削除する
    staging_distribution_config["Enabled"] = False
    staging_distribution_config["ContinuousDeploymentPolicyId"] = ""
    cloudfront.update_distribution(
        Id=staging_distribution_id,
        IfMatch=staging_distribution_etag,
        DistributionConfig=staging_distribution_config,
    )

    return {"Payload": payload}
