# cloudfront-continuous-deployment-stepfunctions

Amazon CloudFront の Continous Deployment を AWS StepFunctions で自動化させる

# Requirements

Mac 環境かつ asdf 管理にて、ツール群は以下の version にて動作することを確認

- Python ^3.10.11

- Poetry ^1.4.1

# Preconditions

事前に Amazon S3 Bucket 等の Origin (含 CNAME) を準備し、CloudFront Distribution をデプロイしておく

デフォルトルートオブジェクトの位置はサンプルとして

```
{color: blue or green}/index.html
```

の書式で設定している (version 等にも設定可能)

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

# Notes

処理の最中に作成される Staging Distribution や Continuous Deployment Policy の削除を追加実装したい

# References

- https://docs.aws.amazon.com/ja_jp/AmazonCloudFront/latest/DeveloperGuide/continuous-deployment.html

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html
