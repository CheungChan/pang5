import os
import time

from logzero import logger

from data import data
from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie, clear_and_send_keys, \
    scroll_to, click, click_by_actionchains

COOKIE_DOMAIN = '.author.maimengjun.com'
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{data["maimeng_username"]}.cookie.json'
MANAGE_URL = 'http://author.maimengjun.com/submission'
AUTH_OK_URL = 'http://author.maimengjun.com/submission'
CREATE_CHAPTER_URL = 'http://author.maimengjun.com/submission/create_chapter'


class MaiMeng:
    def __init__(self):
        pass

    def process(self):
        with open_driver(cookie_domain=COOKIE_DOMAIN,
                         cookie_file=COOKIE_FILE) as driver:
            with track_alert(driver):
                self.driver = driver
                # 处理登录
                add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if not self.login():
                        logger.error('登录失败')
                        return
                store_cookie(driver, COOKIE_FILE)
                logger.info('登录成功')

                # 根据作品名称点击对应的新建章节
                items = driver.find_elements_by_css_selector('#submission > div.container > ul > li')
                for item in items:
                    work_name = item.find_element_by_css_selector('div.content > h3').text
                    logger.debug(f'发现章节{work_name}')
                    if work_name.strip() == data['maimeng_series'].strip():
                        new_chapter = item.find_element_by_css_selector('nav > a:nth-child(2)')
                        new_chapter.click()
                        time.sleep(5)
                handles = driver.window_handles
                if len(handles) == 1:
                    logger.error(f'点击创建章节失败 maimeng_series={data["maimeng_series"]}')
                    return
                else:
                    driver.switch_to_window(handles[1])
                self.publish()

    def login(self):
        login_url = get_current_url()
        clear_and_send_keys(".username-field > input:nth-child(2)", data["maimeng_username"])
        clear_and_send_keys(".password-field > input:nth-child(2)", data["maimeng_password"])
        time.sleep(3)
        self.driver.find_element_by_css_selector(".login-btn").click()
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            input('请处理登录异常，之后按回车键')
        return get_current_url() != login_url

    def publish(self):
        # 章节名称
        self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(1) > div > div.field-input > input[type="text"]').send_keys(
            data['maimeng_title'])
        # 章节介绍
        self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(2) > div > div.field-input > textarea').send_keys(
            data['maimeng_desp'])
        # 展示时间
        if data['maimeng_publish_time']:
            self.driver.find_element_by_css_selector(
                '#create_chapter > div.container > div.inner-container > div:nth-child(3) > div > div.field-input > div > input').send_keys(
                data['maimeng_publish_time'])
            # 点击确定
            self.driver.find_element_by_css_selector(
                'button.el-button.el-picker-panel__link-btn.el-button--default.el-button--mini.is-plain > span').click()
        # 备注
        self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(4) > div > div.field-input > textarea').send_keys(
            data['maimeng_comment'])

        # 漫画原稿
        scroll_to(300)
        self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(5) > div > div.field-input > ul > li > img').click()
        img: str = ' '.join(data['maimeng_pic'])
        logger.info(data)
        logger.info(img)
        os.system(f'D:/uploadImg.exe {img}')
        loading = self.driver.find_element_by_css_selector(
            '#create_chapter > div.container > div.inner-container > div:nth-child(5) > div > div.field-input > ul > div.el-loading-mask')
        while loading.is_displayed():
            time.sleep(2)
        scroll_to()
        # 同意合同
        self.driver.find_element_by_css_selector(
            '#create_chapter > div:nth-child(2) > label > input[type="checkbox"]').click()
        # 提交审核
        time.sleep(2)
        click_by_actionchains('ul.submit > li:nth-child(3) > button.confirm-btn')
        time.sleep(100000)


def main():
    MaiMeng().process()


if __name__ == '__main__':
    main()
