import time

from logzero import logger

from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie

MANAGE_URL = 'http://ac.qq.com/MyComic'
USERNAME = "1042521247"
PASSWORD = "qingdian171717"
COOKIE_DOMAIN = ".qq.com"
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{USERNAME}.cookie.json'


class Tencent:
    def __init__(self):
        pass

    def process(self):
        with open_driver(cookie_domain=".ac.qq.com",
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

                # 点击章节管理
                self.driver.find_element_by_link_text("章节管理").click()

                # 点击新建章节
                self.driver.find_element_by_link_text("新建章节").click()

                # 进入上传章节页面

    def login(self):
        login_url = get_current_url()
        self.driver.switch_to.frame('login_ifr')
        self.driver.find_element_by_css_selector("#switcher_plogin").click()
        self.driver.find_element_by_css_selector("#u").send_keys(USERNAME)
        self.driver.find_element_by_css_selector("#p").send_keys(PASSWORD)
        self.driver.find_element_by_css_selector("#login_button").click()
        time.sleep(3)
        return get_current_url() != login_url


if __name__ == '__main__':
    Tencent().process()
