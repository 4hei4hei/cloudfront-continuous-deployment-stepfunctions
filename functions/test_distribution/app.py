import requests


def lambda_handler(event, context):
    payload = event["Payload"]
    url = payload["Url"]
    test_result = "ng"
    headers = {
        "aws-cf-cd-staging": "true",
    }
    response = requests.get(url, headers=headers)

    # 何らかのテストをさせる
    if response.status_code == 200:
        test_result = "ok"

    return {"Payload": payload | {"TestResult": test_result}}
