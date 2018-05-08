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
    # 接收消息
    i = 0
    logger.info("[x] Received %r" % body)
    rabbitInfo = json.loads(body)

    mysql_id = rabbitInfo['mysql_id']
    db = records.Database(config.MYSQL_URL)

    # 查询章节信息
    chapter_records = db.query('SELECT * FROM  chapter_chapter where id= :id_num', id_num=mysql_id)
    if not len(chapter_records.all()):
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
    if chapter_records[0]['cover_img']:
        if chapter_records[0]['cover_img'][0:4] == 'http':
            content = requests.get(chapter_records[0]['cover_img']).content

        else:
            content = requests.get(
                'http://pang5web.oss-cn-beijing.aliyuncs.com/' + chapter_records[0]['cover_img']).content
        file = BytesIO()
        file.write(content)
        Image.open(file).convert("RGB").save('./images/封面.png')
    # 下载章节图片
    i = 1
    s = chapter_records[0]['chapter_imgs']
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
    # 在本脚本生命周期内,多次重新引入data
    import data
    from importlib import reload
    reload(data)
    data = data.data

    import netEase
    import qingdian
    import tencent
    import mai_meng
    import u17

    # 查询作品信息
    works_records = db.query('SELECT * FROM work_works where id=:work_id', work_id=chapter_records[0]['works_id_id'])
    logger.info(works_records.all())
    if not len(works_records.all()):
        logger.error('没有找到作品信息')
        return

    # 查询用户信息
    user_records = db.query('SELECT * FROM  subscriber_platformsubscriber where id =:id',
                            id=works_records[0]['platform_subsriber_id_id'])
    logger.info(user_records.all())
    if not len(user_records.all()):
        logger.error('没有找到用户信息')
        return



    if user_records[0]['platform'] == 'qingdian':
        data['qingdian_username'] = user_records[0]['platform_username']
        data['qingdian_password'] = user_records[0]['platform_password']
        data['qingdian_series'] = works_records[0]['name']
        data['qingdian_title'] = chapter_records[0]['name']

        qingdian.main(mysql_id)
    elif user_records[0]['platform'] == 'qq':
        data['qq_username'] = user_records[0]['platform_username']
        data['qq_password'] = user_records[0]['platform_password']
        data['qq_comic_id'] = works_records[0]['third_id']
        data['qq_chapter_title'] = chapter_records[0]['name']
        data['qq_use-appoint'] = chapter_records[0]['is_publish_clock']
        data['qq_chapter-publish-time'] = chapter_records[0]['publish_clock_time']
        tencent.main(mysql_id)
    elif user_records[0]['platform'] == 'netEase':
        data['net_username'] = user_records[0]['platform_username']
        data['net_password'] = user_records[0]['platform_password']
        data['net-use-appoint'] = chapter_records[0]['is_publish_clock']
        data['net_series_title'] = works_records[0]['name']
        data['net_title_text'] = chapter_records[0]['name']
        data['net-login'] = user_records[0]['platform_login_type']

        if chapter_records[0]['is_publish_clock']:
            data['net_d'] = chapter_records[0]['publish_clock_time'].split(' ')[0]
            data['net_h'] = chapter_records[0]['publish_clock_time'].split(' ')[1].split(':')[0]
            m_num = int(chapter_records[0]['publish_clock_time'].split(' ')[1].split(':')[1])
            if m_num < 15:
                data['net_m'] = 0
            elif m_num >= 15 and m_num < 30:
                data['net_m'] = 15
            elif m_num >= 30 and m_num < 45:
                data['net_m'] = 30
            elif m_num >= 45 and m_num < 60:
                data['net_m'] = 45

        netEase.main(mysql_id)
    elif user_records[0]['platform'] == 'maimeng':
        data['maimeng_username'] = user_records[0]['platform_username']
        data['maimeng_password'] = user_records[0]['platform_password']
        data['maimeng_series'] = works_records[0]['name']
        data['maimeng_title'] = chapter_records[0]['name']
        data['maimeng_publish_time'] = chapter_records[0]['publish_clock_time']
        mai_meng.main(mysql_id)
    elif user_records[0]['platform'] == 'u17':
        data['u17_username'] = user_records[0]['platform_username']
        data['u17_password'] = user_records[0]['platform_password']
        data['u17_comic_id'] = works_records[0]['third_id']
        data['u17_chapter_name'] = chapter_records[0]['name']
        data['u17_series_name'] = works_records[0]['name']
        u17.main(mysql_id)
    else:
        logger.error('未知平台')

    logger.info('\n\n\n\n')
    # except Exception as e:
    #     logger.error(e)
    #     logger.error('数据错误')
    # finally:
    try:
        os.remove('./images/封面.jpg')
    except:
        pass

    for num in range(i):
        try:
            os.remove('./images/章节/' + str(num + 1) + '.jpg')
        except:
            pass


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
    logger.info(f"Sent success!! {format_json}")


if __name__ == '__main__':
    # row = db.query('SELECT * FROM  chapter_chapter where id= :id_num', id_num=17)
    # print(row[1])
    # insert_rabbit({'mysql_id':13})
    main()
