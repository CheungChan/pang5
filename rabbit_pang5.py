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
from config import LOGFILE_NAME, DATA_CHAPTER_IMAGE, DATA_CLOCK_PUBLISH_DATETIME, DATA_CHAPTER_NAME, DATA_IS_CLOCK, \
    DATA_PASSWORD, DATA_PLATFORM, DATA_THIRD_ID, DATA_USERNAME, DATA_WORKS_IMAGE, DATA_WORKS_NAME, DATA_LOGIN_TYPE, \
    NEED_FLASH_PLATFORM
from utils import get_sorted_imgs

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
    chapter_record = chapter_records[0]

    # 查询作品信息
    works_records = db.query('SELECT * FROM work_works where id=:work_id', work_id=chapter_record['works_id_id'])
    logger.info(works_records.all())
    if not len(works_records.all()):
        logger.error('没有找到作品信息')
        return
    works_record = works_records[0]

    # 查询用户信息
    user_records = db.query('SELECT * FROM  subscriber_platformsubscriber where id =:id',
                            id=works_record['platform_subsriber_id_id'])
    logger.info(user_records.all())
    if not len(user_records.all()):
        logger.error('没有找到用户信息')
        return
    user_record = user_records[0]

    logger.info(f"-------------{user_record['platform']}-----------")
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
    try:
        if chapter_record['cover_img']:
            logger.info(chapter_record['cover_img'])
            if chapter_record['cover_img'][0:4] == 'http':
                content = requests.get(chapter_record['cover_img']).content

            else:
                content = requests.get(
                    'http://pang5web.oss-cn-beijing.aliyuncs.com/' + chapter_record['cover_img']).content
            file = BytesIO()
            file.write(content)
            Image.open(file).convert("RGB").save('./images/封面.png')
    except Exception as e:
        logger.error(e)
        logger.error('封面图片下载失败')
        return
    # 下载章节图片
    try:
        i = 1
        s = chapter_record['chapter_imgs']
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
    except Exception as e:
        logger.error(e)
        logger.error('章节图片下载失败')
    # 在本脚本生命周期内,多次重新引入data
    import data
    from importlib import reload
    reload(data)
    data = data.data

    # 赋值data

    data[DATA_PLATFORM] = user_record['platform']
    data[DATA_USERNAME] = user_record['platform_username']
    data[DATA_PASSWORD] = user_record['platform_password']
    data[DATA_WORKS_NAME] = works_record['name']
    data[DATA_CHAPTER_NAME] = chapter_record['name']
    data[DATA_THIRD_ID] = works_record['third_id']
    data[DATA_IS_CLOCK] = chapter_record['is_publish_clock']
    data[DATA_CLOCK_PUBLISH_DATETIME] = chapter_record['publish_clock_time']
    data[DATA_LOGIN_TYPE] = user_record['platform_login_type']
    data[DATA_WORKS_IMAGE] = os.path.join(pwd, 'images', '封面.png')

    if user_record['platform'] in NEED_FLASH_PLATFORM:
        data[DATA_CHAPTER_IMAGE] = [f'"{os.path.join(pwd,"images","章节",d)}"' for d in
                                    get_sorted_imgs(os.path.join(pwd, 'images', '章节'))]
    else:
        data[DATA_CHAPTER_IMAGE] = [f'{os.path.join(pwd,"images" ,"章节",d)}' for d in
                                    get_sorted_imgs(os.path.join(pwd, "images", "章节"))]
    logger.info(data)
    import netEase
    import qingdian
    import qq
    import mai_meng
    import u17

    platforms = {
        'netEase': netEase,
        'qingdian': qingdian,
        'maimeng': mai_meng,
        'qq': qq,
        'u17': u17,
    }
    if data[DATA_PLATFORM] in platforms:
        p = platforms[data[DATA_PLATFORM]]
        reload(p)
        # 不许重新导入平台模块,这样平台模块里的data才是最新的
        p.main(mysql_id)
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
