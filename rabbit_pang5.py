#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-4-2 下午5:31
# @Author  : huanggz
# @File    : rabbit_pang5.py
# @Software: PyCharm
# code is far away from bugs with the god animal protecting
import json
import os
from io import BytesIO

import pika
import records
import requests
from PIL import Image
from logzero import logger

import config
import netEase
import qingdian
import tencent

db = records.Database(config.TEST_MYSQL_URL)


def main():
    credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config.RABBITMQ_HTOS, config.RABBITMQ_POST, '/', credentials))
    channel = connection.channel()
    channel.queue_declare(queue='pang5_web', durable=True)
    channel.basic_consume(callback, queue='pang5_web', no_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def callback(ch, method, properties, body):
    logger.info("[x] Received %r" % body)
    rabbitInfo = json.loads(body)

    try:
        mysql_id = rabbitInfo['mysql_id']
        row = db.query('SELECT * FROM  chapter_chapter where id= :id_num', id_num=mysql_id)
        print(row[0])
        # 下载封面
        if row[0]['cover_img']:
            content = requests.get('http://pang5web.oss-cn-beijing.aliyuncs.com/' + row[0]['cover_img']).content
            file = BytesIO()
            file.write(content)
            Image.open(file).convert("RGB").save('./images/封面.jpg')
        i = 1
        for img in json.loads(row[0]['chapter_imgs']):
            content = requests.get('http://pang5web.oss-cn-beijing.aliyuncs.com/' + img).content
            file = BytesIO()
            file.write(content)
            Image.open(file).convert("RGB").save('./images/章节/' + str(i) + ".jpg")
            i += 1
            # 平台
            userinfo = db.query('SELECT * FROM subscriber_platformsubscriber where id=:platform_subsriber_id_id',
                                platform_subsriber_id_id=row[0]['platform_subsriber_id_id'])
        # if userinfo[0]['platform'] == 'qingdian':
        #     qingdian.main()
        # elif userinfo[0]['platform'] == 'qq':
        #     tencent.main()
        # elif userinfo[0]['platform'] == 'netEase':
        #     netEase.main()
        # else:
        #     logger.error('未知平台')

        if row[0]['cover_img']:
            os.remove('./images/封面.jpg')
        for i in  range(i):
            os.remove('./images/章节/' + str(i+1) + '.jpg')
    except Exception as e:
        print(e)
        logger.error('数据错误')


def insert_rabbit(format):
    credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config.RABBITMQ_HTOS, config.RABBITMQ_POST, '/', credentials))
    channel = connection.channel()

    # 声明queue
    channel.queue_declare(queue='pang5_web', durable=True)
    # print(type(mysql_format))

    format_json = json.dumps(format)
    channel.basic_publish(exchange='',
                          routing_key='pang5_web',
                          body=format_json, )
    logger.info("Sent success!!")


if __name__ == '__main__':
    insert_rabbit({'mysql_id': 6})
    main()
