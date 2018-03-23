import json
import os
from datetime import datetime
import time
from logzero import logger
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException, WebDriverException

from config import USE_FACE, CHROME_DRIVER_PATH, PHANTOMJS_PATH, SCREENSHOT_PATH

g_driver = None


class open_driver(object):
    def __init__(self, width=1920, height=7000, cookie_domain=None, load_image=False):
        self.width = width
        self.height = height
        self.cookie_domain = cookie_domain
        self.load_image = load_image
        if self.cookie_domain:
            self.cookie_file = os.path.join(os.path.expanduser('~'), self.cookie_domain[1:] + '.json')
            if not os.path.exists(self.cookie_file):
                raise Exception(f'{self.cookie_file} 不存在，请设置')

    def __enter__(self):
        global g_driver
        if USE_FACE:
            self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)
            # self.driver = webdriver.Firefox(executable_path='/usr/bin/geckodriver')

            logger.info('chrome浏览器打开')
            self.driver.get('http://www.baidu.com')
        else:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
            )
            service_args = []

            if not self.load_image:
                service_args.append('--load-images=no')
            service_args.append('--disk-cache=yes')
            service_args.append('--ignore-ssl-errors=true')
            self.driver = webdriver.PhantomJS(PHANTOMJS_PATH, desired_capabilities=dcap, service_args=service_args)
            logger.info('phantomjs浏览器打开')
        self.driver.set_window_size(self.width, self.height)
        self.add_cookie()
        js = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.scroll_buttom = lambda: self.driver.execute_script(js)
        g_driver = self.driver
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            self.driver.get_screenshot_as_file(
                f"{SCREENSHOT_PATH}/excep_{datetime.now().strftime('%Y-%m-%d %H %M %S')}.png")
        self.store_cookie()
        logger.info("浏览器关闭")
        self.driver.close()
        self.driver.quit()
        if exc_tb:
            logger.error("出现异常")
            logger.error(exc_type)
            logger.error(exc_val)
            logger.error(exc_tb)
            return False

    def add_cookie(self):
        if not self.cookie_domain:
            return
        logger.info('加载cookie')
        self.driver.delete_all_cookies()
        cookies = json.load(open(self.cookie_file, 'r'))
        for c in cookies:
            if c.get('domain') != self.cookie_domain:
                continue
            self.driver.add_cookie(c)
        logger.info('加载完成')

    def store_cookie(self):
        if not self.cookie_domain:
            return
        logger.info('存储cookie')
        new_cookies = self.driver.get_cookies()
        json.dump(new_cookies, open(self.cookie_file, 'w'))
        logger.info('加载完成')


class track_alert(object):
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == UnexpectedAlertPresentException:
            if exc_tb:
                self.driver.get_screenshot_as_file(
                    f"{SCREENSHOT_PATH}/alert_{datetime.now().strftime('%Y-%m-%d %H %M %S')}.png")
            import re
            msg = re.findall(r'{Alert text : (.*)}', exc_val.msg)[0]
            logger.error(msg)
            return True


def refresh_recursion(url, num=3):
    if num == 0:
        return False
    try:
        logger.info(f'refresh:{num}')
        g_driver.get(url)
        return True
    except:
        try:
            g_driver.refresh()
        except Exception as e:
            logger.warning(f'refresh: {url} {e}')
    return refresh_recursion(url, num - 1)


def get(url, sleep=2):
    try:
        logger.info(f'get:{url}')
        g_driver.implicitly_wait(10)
        g_driver.get(url)
    except TimeoutException as e:
        g_driver.logger.warning(f'get: {url} {e}')
        try:
            refresh_recursion(url)
        except TimeoutException as e2:
            return True
        time.sleep(sleep)
    return True


def get_current_url():
    try:
        g_driver.implicitly_wait(10)
        # current_url = execute_js('return window.location.href;')
        current_url = g_driver.current_url
    except TimeoutException:
        current_url = ''
    return current_url
