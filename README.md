# cloudfront-continuous-deployment-stepfunctions

Amazon CloudFront の Continous Deployment を AWS StepFunctions で自動化させる

# Requirements

Mac 環境かつ asdf 管理にて、ツール群は以下の version にて動作することを確認

- AWS SAM CLI 1.100.0

- Python ^3.11.5

- Poetry ^1.6.1

# Preconditions

本リポジトリの StepFunctions では Origin を S3 とする CloudFront を前提としている

そのため事前に Origin となる S3 の以下のパスに index.html を 2 種類用意する

- s3://{S3_BUCKET_NAME}/blue/index.html

- s3://{S3_BUCKET_NAME}/green/index.html

いずれかを CloudFront 経由で閲覧できる状態としておく

# How to use

1. AWS SAM CLI にて本 SAM テンプレートをデプロイする

2. デプロイされた StepFucntions を以下フォーマットの json を入力として実行する

```
{
  "Url": "https://{hoge.fuga}",
  "PrimaryDistributionId": "{既にデプロイされている PrimaryDistribution の ID}",
  "StagingDistributionColor": "{blue or green}"
}
```

以下のフローを辿る StateMachine の処理が起動する

![StateMachine Sample](./statemachine_flow.png)

# References

- https://docs.aws.amazon.com/ja_jp/AmazonCloudFront/latest/DeveloperGuide/continuous-deployment.html

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html
