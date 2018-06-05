# -*- coding: utf-8 -*-
__author__ = 'cheungchan'
__date__ = '2018/6/5 12:17'

import base64
import json
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen


def image_recog(img_path, v_type='ne5'):
    """
    图形验证码调用服务识别
    :param img_path:
    :param v_type: 图形验证码类型（n4：4位纯数字，n5：5位纯数字，n6:6位纯数字，e4：4位纯英文，e5：5位纯英文，e6：6位纯英文，
    ne4：4位英文数字，ne5：5位英文数字，ne6：6位英文数字），请准确填写，以免影响识别准确性。
    :return:
    """

    f = open(img_path, 'rb')  # 二进制方式打开图文件
    ls_f = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
    f.close()

    host = 'http://txyzmsb.market.alicloudapi.com'
    path = '/yzm'
    appcode = 'fec023302d074cd08ca51aaf8f660ba0'
    bodys = {}
    url = host + path

    bodys['v_pic'] = ls_f
    bodys['v_type'] = v_type
    post_data = urlencode(bodys).encode('utf-8')

    request = Request(url, post_data)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    response = urlopen(request)
    content = json.loads(response.read().decode('utf-8'))

    print(content)
    result = content.get('v_code')
    ok = content.get('errCode') == 0
    return result, ok


if __name__ == '__main__':
    result, ok = image_recog('/Users/chenzhang/Pictures/pin.png')
    print(result, ok)
