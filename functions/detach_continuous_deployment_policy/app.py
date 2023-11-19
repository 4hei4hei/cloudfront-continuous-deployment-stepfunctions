import boto3
from botocore.config import Config


config = Config(retries={"max_attempts": 10, "mode": "standard"})
cloudfront = boto3.client("cloudfront", config=config)


def lambda_handler(event, context):
    payload = event["Payload"]
    primary_distribution_id = payload["PrimaryDistributionId"]
    staging_distribution_id = payload["StagingDistributionId"]
    continuous_deployment_policy_id = payload["ContinuousDeploymentPolicyId"]
    continuous_deployment_policy_etag = (
        cloudfront.get_continuous_deployment_policy_config(
            Id=continuous_deployment_policy_id
        )["ETag"]
    )

    # PrimaryDistribution の ContinuousDeploymentPolicy を外す (Id を空に設定して Update をかける)
    primary_distribution_config = cloudfront.get_distribution_config(
        Id=primary_distribution_id
    )
    primary_distribution_etag = primary_distribution_config["ETag"]
    update_primary_distribution_config = primary_distribution_config[
        "DistributionConfig"
    ]
    update_primary_distribution_config["ContinuousDeploymentPolicyId"] = ""
    cloudfront.update_distribution(
        Id=primary_distribution_id,
        IfMatch=primary_distribution_etag,
        DistributionConfig=update_primary_distribution_config,
    )

    # ContinuousDeploymentPolicy (継続的デプロイメント用の設定) を無効化する
    staging_distribution = cloudfront.get_distribution(Id=staging_distribution_id)
    traffic_config = {
        "Type": "SingleHeader",
        "SingleHeaderConfig": {"Header": "aws-cf-cd-staging", "Value": "true"},
    }
    continuous_deployment_policy_config = {
        "StagingDistributionDnsNames": {
            "Quantity": 1,
            "Items": [
                staging_distribution["Distribution"]["DomainName"],
            ],
        },
        "Enabled": False,
        "TrafficConfig": traffic_config,
    }
    cloudfront.update_continuous_deployment_policy(
        Id=continuous_deployment_policy_id,
        IfMatch=continuous_deployment_policy_etag,
        ContinuousDeploymentPolicyConfig=continuous_deployment_policy_config,
    )

    return {"Payload": payload}
