import time
import os
from logzero import logger
from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie, clear_and_send_keys, \
    use_flash, scroll_to, click_by_pg
from data import data

COOKIE_DOMAIN = 'author.maimengjun.com'
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{data["maimeng_username"]}.cookie.json'
MANAGE_URL = 'http://author.maimengjun.com/submission'
AUTH_OK_URL = 'http://author.maimengjun.com/submission'


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
                pass


    def login(self):
        login_url = get_current_url()
        clear_and_send_keys(".username-field > input:nth-child(2)", data["maimeng_username"])
        clear_and_send_keys(".password-field > input:nth-child(2)", data["maimeng_password"])
        time.sleep(2)
        self.driver.find_element_by_css_selector(".login-btn").click()
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            input('请处理登录异常，之后按回车键')
        return get_current_url() != login_url


if __name__ == '__main__':
    MaiMeng().process()
