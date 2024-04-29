import boto3
import json
import uuid


cloudfront = boto3.client("cloudfront")
ssm = boto3.client("ssm")


def lambda_handler(event, context):
    payload = event["Payload"]
    primary_distribution_id = payload["PrimaryDistributionId"]
    configs_for_deployment_name = payload["DeploymentConfigName"]

    # Primary distribution を基に Staiging distribution を作成する
    primary_distribution_config = cloudfront.get_distribution_config(
        Id=primary_distribution_id
    )
    staging_caller_reference = str(uuid.uuid4())
    staging_distribution = cloudfront.copy_distribution(
        PrimaryDistributionId=primary_distribution_id,
        Staging=True,
        IfMatch=primary_distribution_config["ETag"],
        CallerReference=staging_caller_reference,
    )

    # Staging distribution の ID と Distribution config 設定をまるっと変数化 (後工程で流用するため)
    staging_distribution_id = staging_distribution["Distribution"]["Id"]
    staging_distribution_config = cloudfront.get_distribution_config(
        Id=staging_distribution_id
    )["DistributionConfig"]

    # 流用する Distribution config の中で上書きしたい項目をここで上書きしておく
    # 変更箇所は SSM Parameter Store に登録する
    configs_for_deployment = json.loads(
        ssm.get_parameter(Name=configs_for_deployment_name, WithDecryption=True)[
            "Parameter"
        ]["Value"]
    )
    for config in configs_for_deployment["DistributionConfig"]:
        staging_distribution_config[config] = configs_for_deployment[
            "DistributionConfig"
        ].get(config)

    # 作成した Staging distribution を Update する
    cloudfront.update_distribution(
        Id=staging_distribution_id,
        IfMatch=staging_distribution["ETag"],
        DistributionConfig=staging_distribution_config,
    )

    # Continuous deployment policy (継続的デプロイメント用の設定) を作成する
    staging_traffic_config = {
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
        "Enabled": True,
        "TrafficConfig": staging_traffic_config,
    }

    continuous_deployment_policy = cloudfront.create_continuous_deployment_policy(
        ContinuousDeploymentPolicyConfig=continuous_deployment_policy_config
    )

    # 作成したポリシを Primary distribution にアタッチして Update をかける
    primary_distribution_config = cloudfront.get_distribution_config(
        Id=primary_distribution_id
    )
    update_distribution_config = primary_distribution_config["DistributionConfig"]
    update_distribution_config[
        "ContinuousDeploymentPolicyId"
    ] = continuous_deployment_policy["ContinuousDeploymentPolicy"]["Id"]
    cloudfront.update_distribution(
        Id=primary_distribution_id,
        IfMatch=primary_distribution_config["ETag"],
        DistributionConfig=update_distribution_config,
    )

    return {
        "Payload": payload
        | {
            "ContinuousDeploymentPolicyId": continuous_deployment_policy[
                "ContinuousDeploymentPolicy"
            ]["Id"],
            "StagingDistributionId": staging_distribution_id,
            "StagingCallerReference": staging_caller_reference,
        }
    }
