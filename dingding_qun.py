import json

import requests

url = 'https://oapi.dingtalk.com/robot/send?access_token=7ce99d5e029f51b5f2570c3301dedb03fde41bee494dc650c633e9f6bdc09b60'


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
    requests.post(url, data=data, headers={'Content-Type': 'application/json'})


def dingSendMarkdown(title, markdown):
    data = json.dumps({
        "msgtype": "markdown",
        "markdown": {"title": title,
                     "text": markdown
                     },
        "at": {
            "atMobiles": [],
            "isAtAll": False
        }
    })
    requests.post(url, data=data, headers={'Content-Type': 'application/json'})



if __name__ == '__main__':
    line = "你们好"
    # dingdSendMsg(line)
    # print(line)
    title = '杭州天气'
    markdown = "#### 杭州天气  \n > 9度，@1825718XXXX 西北风1级，空气良89，相对温度73%\n\n > ![screenshot](http://i01.lw.aliimg.com/media/lALPBbCc1ZhJGIvNAkzNBLA_1200_588.png)\n  > ###### 10点20分发布 [天气](http://www.thinkpage.cn/) "
    dingSendMarkdown(title, markdown)
