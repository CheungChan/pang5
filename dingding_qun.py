import json

import requests


def dingdSendMsg(msg):
    data = json.dumps({
        "msgtype": "text",
        "text": {
            "content": msg
        },
        "at": {
            'atMobiles': [],
            "isAtAll": False
        }
    })
    url = 'https://oapi.dingtalk.com/robot/send?access_token=7ce99d5e029f51b5f2570c3301dedb03fde41bee494dc650c633e9f6bdc09b60'
    requests.post(url, data=data, headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    line = "你们好"
    dingdSendMsg(line)
    print(line)
