import os
import time

import logzero
from logzero import logger

from config import LOGFILE_NAME, DATA_CHAPTER_IMAGE, DATA_CLOCK_PUBLISH_DATETIME, \
    DATA_IS_CLOCK, DATA_CHAPTER_NAME, DATA_WORKS_NAME, DATA_PASSWORD, DATA_USERNAME, DATA_PLATFORM, \
    PLATFORM_STATUS_AUTH_OK, PLATFORM_STATUS_AUTH_FAIL
from data import data
from utils import open_driver, track_alert, get, get_current_url, clear_and_send_keys, \
    scroll_to, click_by_actionchains, g_mysqlid, Pang5Exception, update_login_status

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
MANAGE_URL = 'http://author.maimengjun.com/submission'
AUTH_OK_URL = 'http://author.maimengjun.com/submission'
CREATE_CHAPTER_URL = 'http://author.maimengjun.com/submission/create_chapter'


class MaiMeng:
    def __init__(self):
        logger.info(data)

    def process(self, mysql_id):
        g_mysqlid["mysql_id"] = mysql_id
        with open_driver(browser='firefox') as driver:
            with track_alert(driver):
                self.driver = driver
                # 处理登录
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if not self.login():
                        raise Pang5Exception('登录失败')
                logger.info('登录成功')

                # 根据作品名称点击对应的新建章节
                items = driver.find_elements_by_css_selector('#submission > div.container > ul > li')
                for item in items:
                    work_name = item.find_element_by_css_selector('div.content > h3').text
                    logger.debug(f'发现作品{work_name}')
                    if work_name.strip() == data[DATA_WORKS_NAME].strip():
                        new_chapter = item.find_element_by_css_selector('nav > a:nth-child(2)')
                        new_chapter.click()
                        time.sleep(5)
                handles = driver.window_handles
                if len(handles) == 1:
                    logger.error(f'点击创建章节失败 maimeng_series={data[DATA_WORKS_NAME]}')
                    return
                else:
                    driver.switch_to_window(handles[1])
                self.publish()

    def login(self) -> bool:
        login_url = get_current_url()
        clear_and_send_keys(".username-field > input:nth-child(2)", data[DATA_USERNAME])
        clear_and_send_keys(".password-field > input:nth-child(2)", data[DATA_PASSWORD])
        time.sleep(3)
        self.driver.find_element_by_css_selector(".login-btn").click()
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            logger.error(get_current_url())
            status = PLATFORM_STATUS_AUTH_FAIL
            update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                platform_password=data[DATA_PASSWORD], platform_status=status)
            raise Pang5Exception("登录异常")
        status = PLATFORM_STATUS_AUTH_OK
        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                            platform_password=data[DATA_PASSWORD], platform_status=status)
        return True

    def publish(self):
        # 章节名称
        self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(1) > div > div.field-input > input[type="text"]').send_keys(
            data[DATA_CHAPTER_NAME])
        # # 章节介绍
        # self.driver.find_element_by_css_selector(
        #     '#create_chapter > div.container > div.inner-container > div:nth-child(2) > div > div.field-input > textarea').send_keys(
        #     data['maimeng_desp'])
        # 展示时间
        if data[DATA_IS_CLOCK]:
            self.driver.find_element_by_css_selector(
                '#create_chapter > div.container > div.inner-container > div:nth-child(3) > div > div.field-input > div > input').send_keys(
                data[DATA_CLOCK_PUBLISH_DATETIME])
            # 点击确定
            time.sleep(2)
            js = 'jQuery("button.el-button:nth-child(2)").click();'
            self.driver.execute_script(js)
        # # 备注
        # self.driver.find_element_by_css_selector(
        #     '#create_chapter > div.container > div.inner-container > div:nth-child(4) > div > div.field-input > textarea').send_keys(
        #     data['maimeng_comment'])

        # 漫画原稿
        # scroll_to()
        self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(5) > div > div.field-input > ul > li > img').click()
        img: str = ' '.join(data[DATA_CHAPTER_IMAGE])
        logger.info(data)
        logger.info(img)
        cmd = f'D:/uploadImg.exe 文件上传 {img}'
        logger.info(cmd)
        os.system(cmd)
        loading = self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(5) > div > div.field-input > ul > div.el-loading-mask')
        scroll_to()
        while loading.is_displayed():
            time.sleep(2)
        scroll_to()
        # 同意合同
        self.driver.find_element_by_css_selector(
            '#create_chapter > div:nth-child(2) > label > input[type="checkbox"]').click()
        scroll_to()
        # 提交审核
        time.sleep(2)
        click_by_actionchains('ul.submit > li:nth-child(3) > button.confirm-btn')
        time.sleep(3)


def main(mysql_id):
    MaiMeng().process(mysql_id)


if __name__ == '__main__':
    main(10000)
