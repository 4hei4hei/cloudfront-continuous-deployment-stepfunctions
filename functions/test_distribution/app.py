import requests


def lambda_handler(event, context):
    payload = event["Payload"]
    url = payload["Url"]
    test_result = "ng"

    # Staging distribution へリクエストを送るためのヘッダを引数に設定
    headers = {
        "aws-cf-cd-staging": "true",
    }
    # ヘッダ設定を使ってリクエストを送る
    response = requests.get(url, headers=headers)

    # 何らかのテストをさせる
    if response.status_code == 200:
        test_result = "ok"

    return {"Payload": payload | {"TestResult": test_result}}
