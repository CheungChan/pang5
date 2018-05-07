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
import logzero
import pika
import records
import requests
from PIL import Image
from logzero import logger

import config
from config import LOGFILE_NAME

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)

db = records.Database(config.MYSQL_URL)

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

    mysql_id = rabbitInfo['mysql_id']
    row = db.query('SELECT * FROM  chapter_chapter where id= :id_num', id_num=mysql_id)
    if not len(row.all()):
        return

    # 清空文件夹

    for root, dirs, files in os.walk('./images/章节'):
        for name in files:
            if name != '.gitkeep':
                os.remove(os.path.join(root, name))
                logger.info(f'删除图片{os.path.join(root, name)}')

    for root, dirs, files in os.walk('./images/'):
        for name in files:
            if name not in ['.gitkeep', '章节']:
                os.remove(os.path.join(root, name))
                logger.info(f'删除图片{os.path.join(root, name)}')

    # 下载封面
    if row[0]['cover_img']:
        if row[0]['cover_img'][0:4] == 'http':
            content = requests.get(row[0]['cover_img']).content

        else:
            content = requests.get('http://pang5web.oss-cn-beijing.aliyuncs.com/' + row[0]['cover_img']).content
        file = BytesIO()
        file.write(content)
        Image.open(file).convert("RGB").save('./images/封面.png')
    i = 1
    s = row[0]['chapter_imgs']
    for img in json.loads(s):
        logger.info(img)
        if img[0:4] == "http":
            content = requests.get(img).content

        else:
            url = 'http://pang5web.oss-cn-beijing.aliyuncs.com/' + img
            logger.info(url)
            content = requests.get(url).content
        file = BytesIO()
        file.write(content)
        Image.open(file).convert("RGB").save(os.path.join(pwd, "images", "章节", str(i) + os.path.splitext(img)[1]))
        i += 1
    from data import data
    import netEase
    import qingdian
    import tencent
    import mai_meng
    # 平台
    works_info = db.query('SELECT * FROM work_works where id=:work_id', work_id=row[0]['works_id_id'])
    print(works_info.all())
    if not len(works_info.all()):
        return
    userinfo = db.query('SELECT * FROM  subscriber_platformsubscriber where id =:id',
                        id=works_info[0]['platform_subsriber_id_id'])
    print(userinfo.all())
    if userinfo[0]['platform'] == 'qingdian':
        data['qingdian_username'] = userinfo[0]['platform_username']
        data['qingdian_password'] = userinfo[0]['platform_password']
        data['qingdian_series'] = works_info[0]['name']
        data['qingdian_title'] = row[0]['name']

        qingdian.main(mysql_id)
    elif userinfo[0]['platform'] == 'qq':
        data['qq_username'] = userinfo[0]['platform_username']
        data['qq_password'] = userinfo[0]['platform_password']
        data['qq_comic_id'] = works_info[0]['third_id']
        data['qq_chapter_title'] = row[0]['name']
        data['qq_use-appoint'] = row[0]['is_publish_clock']
        data['qq_chapter-publish-time'] = row[0]['publish_clock_time']
        tencent.main(mysql_id)
    elif userinfo[0]['platform'] == '':
        data['net_username'] = userinfo[0]['platform_username']
        data['net_password'] = userinfo[0]['platform_password']
        data['net-use-appoint'] = row[0]['is_publish_clock']
        data['net_series_title'] = works_info[0]['name']
        data['net_title_text'] = row[0]['name']
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

        netEase.main(mysql_id)
    elif userinfo[0]['platform'] == 'maimeng':
        data['maimeng_username'] = userinfo[0]['platform_username']
        data['maimeng_password'] = userinfo[0]['platform_password']
        data['maimeng_series'] = works_info[0]['name']
        data['maimeng_title'] = row[0]['name']
        data['maimeng_publish_time'] = row[0]['publish_clock_time']
        mai_meng.main(mysql_id)
    elif userinfo[0]['platform'] == 'u17':
        data['u17_username'] = userinfo[0]['platform_username']
        data['u17_password'] = userinfo[0]['platform_password']
        data['u17_comic_id'] = works_info[0]['third_id']
        data['u17_chapter'] = row[0]['name']
        data['u17_series'] = works_info[0]['name']
    else:
        logger.error('未知平台')

    # except Exception as e:
    #     logger.error(e)
    #     logger.error('数据错误')
    # finally:
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
    # row = db.query('SELECT * FROM  chapter_chapter where id= :id_num', id_num=17)
    # print(row[1])
    # insert_rabbit({'mysql_id':13})
    main()
