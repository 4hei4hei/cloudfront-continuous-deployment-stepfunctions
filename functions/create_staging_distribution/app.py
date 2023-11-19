import boto3
import uuid
from botocore.config import Config


config = Config(retries={"max_attempts": 10, "mode": "standard"})
cloudfront = boto3.client("cloudfront", config=config)


def lambda_handler(event, context):
    payload = event["Payload"]
    primary_distribution_id = payload["PrimaryDistributionId"]
    staging_distribution_color = payload["StagingDistributionColor"]

    # PrimaryDistribution を基に StaigingDistribution を作成する
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

    # StagingDistribution の ID と Config 設定をまるっと変数化 (後工程で流用するため)
    staging_distribution_id = staging_distribution["Distribution"]["Id"]
    staging_distribution_config = cloudfront.get_distribution_config(
        Id=staging_distribution_id
    )["DistributionConfig"]

    # 流用する Config のうち、上書きしたいものをここで上書きしておく
    # 今回は Staging であることを判定する項目を True とし、インデックスドキュメントの配置場所を更新させる
    staging_distribution_config["Staging"] = True
    staging_distribution_config[
        "DefaultRootObject"
    ] = f"{staging_distribution_color}/index.html"

    # 作成した StagingDistribution を Update する
    cloudfront.update_distribution(
        Id=staging_distribution_id,
        IfMatch=staging_distribution["ETag"],
        DistributionConfig=staging_distribution_config,
    )

    # ContinuousDeploymentPolicy (継続的デプロイメント用の設定) を作成する
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

    # 作成したポリシを PrimaryDistribution にアタッチして Update をかける
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
