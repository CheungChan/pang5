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
import traceback
import pika
import records
import requests
from PIL import Image
from logzero import logger

import config

from data import data
import netEase
import qingdian
import tencent
import mai_meng

db = records.Database(config.TEST_MYSQL_URL)

pwd = os.path.abspath(os.curdir)


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
    i = 0
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
            Image.open(file).convert("RGB").save(os.path.join(pwd, "images", "章节", str(i) + ".jpg"))
            i += 1
            # 平台
            userinfo = db.query('SELECT * FROM subscriber_platformsubscriber where id=:platform_subsriber_id_id',
                                platform_subsriber_id_id=row[0]['platform_subsriber_id_id'])
        if userinfo[0]['platform'] == 'qingdian':
            data['qingdian_username'] = userinfo[0]['platform_username']
            data['qingdian_password'] = userinfo[0]['platform_password']
            data['qingdian_series'] = row[0]['works_name']
            data['qingdian_title'] = row[0]['chapter_name']

            qingdian.main()
        elif userinfo[0]['platform'] == 'qq':
            data['qq_username'] = userinfo[0]['platform_username']
            data['qq_password'] = userinfo[0]['platform_password']
            data['qq_comic_id'] = row[0]['works_id']
            data['qq_chapter_title'] = row[0]['chapter_name']
            data['qq_use-appoint'] = row[0]['is_publish_clock']
            data['qq_chapter-publish-time'] = row[0]['publish_clock_time']
            tencent.main()
        elif userinfo[0]['platform'] == 'netEase':
            data['net_username'] = userinfo[0]['platform_username']
            data['net_password'] = userinfo[0]['platform_password']
            data['net-use-appoint'] = row[0]['is_publish_clock']
            data['net_series_title'] = row[0]['works_name']
            data['net_title_text'] = row[0]['chapter_name']
            data['net-login'] = userinfo[0]['platform_login_type']

            if row[0]['is_publish_clock']:
                data['net_d'] = row[0]['publish_clock_time'].split(' ')[0]
                data['net_h'] = row[0]['publish_clock_time'].split(' ')[1].split(':')[0]
                m_num = int(row[0]['publish_clock_time'].split(' ')[1].split(':')[1])
                if m_num < 15:
                    data['net_m'] = 0
                elif m_num >= 15 and m_num < 30:
                    data['net_m'] = 15
                elif m_num >= 30 and m_num < 45:
                    data['net_m'] = 30
                elif m_num >= 45 and m_num < 60:
                    data['net_m'] = 45

            netEase.main()
        elif userinfo[0]['platform'] == 'maimeng':
            data['maimeng_username'] = userinfo[0]['platform_username']
            data['maimeng_password'] = userinfo[0]['platform_password']
            data['maimeng_series'] = row[0]['works_name']
            data['maimeng_title'] = row[0]['chapter_name']
            data['maimeng_publish_time'] = row[0]['publish_clock_time'].split(' ')[0]
            mai_meng.main()
        else:
            logger.error('未知平台')

    except Exception as e:
        print(e)
        logger.error('数据错误')
    finally:
        try:
            os.remove('./images/封面.jpg')
        except:
            logger.error('no find')

        for num in range(i):
            try:
                os.remove('./images/章节/' + str(num + 1) + '.jpg')
            except:
                logger.error('no find')


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
    # insert_rabbit({'mysql_id': 14})
    main()
    # print(os.path.join(pwd,"images","章节","aa.jpg"))
