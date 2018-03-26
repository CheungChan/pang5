import json
import os
import time
from datetime import datetime

from logzero import logger
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import USE_FACE, CHROME_DRIVER_PATH, PHANTOMJS_PATH, SCREENSHOT_PATH, WAIT_CLICKABLE, WAIT_PRESENCE, \
    WAIT_VISIABLITY

g_driver = None


class open_driver(object):
    def __init__(self, width=1920, height=7000, cookie_domain=None, load_image=False, cookie_file=None,
                 browser='chrome'):
        self.width = width
        self.height = height
        self.cookie_domain = cookie_domain
        self.load_image = load_image
        if self.cookie_domain:
            self.cookie_file = cookie_file
        self.browser = browser

    def __enter__(self):
        global g_driver
        if USE_FACE:
            if self.browser == 'chrome':
                self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)

                logger.info('chrome浏览器打开')
                self.driver.get('http://www.baidu.com')
            elif self.browser == 'firefox':
                self.driver = webdriver.Firefox(executable_path='/usr/bin/geckodriver')
                logger.info('firefox浏览器打开')
                # self.driver.get('http://www.baidu.com')

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
        js = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.scroll_buttom = lambda: self.driver.execute_script(js)
        g_driver = self.driver
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            self.driver.get_screenshot_as_file(
                f"{SCREENSHOT_PATH}/excep_{datetime.now().strftime('%Y-%m-%d %H %M %S')}.png")
        logger.info("浏览器关闭")
        self.driver.close()
        self.driver.quit()
        if exc_tb:
            logger.error("出现异常")
            logger.error(exc_type)
            logger.error(exc_val)
            logger.error(exc_tb)
            return False


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


def add_cookie(cookie_domain, driver, cookie_file):
    if not os.path.exists(cookie_file):
        return False
    logger.info('加载cookie')
    driver.delete_all_cookies()
    cookies = json.load(open(cookie_file, 'r'))
    for c in cookies:
        if c.get('domain') != cookie_domain:
            continue
        driver.add_cookie(c)
    logger.info('加载完成')
    return True


def store_cookie(driver, cookie_file):
    logger.info('存储cookie')
    new_cookies = driver.get_cookies()
    json.dump(new_cookies, open(cookie_file, 'w'))
    logger.info('加载完成')


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
    logger.debug(f'current_url= {current_url}')
    return current_url


def cookie_from_chrome_to_json(cookie_str, domain, username):
    cookie_list = cookie_str.split(';')
    cookies = []
    for c in cookie_list:
        name, value = c.split('=', maxsplit=1)
        cookie = {'domain': domain, 'name': name, 'value': value, 'path': '/'}
        cookies.append(cookie)
    cookie_file = f'cookies/{domain[1:]}_{username}.json'
    json.dump(cookies, open(cookie_file, 'w'))
    logger.info(f'持久化{cookie_file}')


def __wait_ele(xpath, max_sec, _type):
    if _type == WAIT_PRESENCE:
        element_located = expected_conditions.presence_of_element_located
    elif _type == WAIT_VISIABLITY:
        element_located = expected_conditions.visibility_of_element_located
    elif _type == WAIT_CLICKABLE:
        element_located = expected_conditions.element_to_be_clickable
    else:
        raise Exception("方法调用错误，请检查_type参数")

    try:
        WebDriverWait(g_driver, max_sec, 0.5).until(element_located((By.XPATH, xpath)))
        return True
    except Exception as e:
        logger.error(f'超过{max_sec}秒 {xpath} 不能显示，错误 {e}')
        return False


def __wait_ele_clickable(css, max_sec=20):
    return __wait_ele(css, max_sec, WAIT_CLICKABLE)


def click(css):
    if __wait_ele_clickable(css):
        g_driver.find_element(By.CSS_SELECTOR, css).click()
        return True
    else:
        logger.error(f'点击没有找到定位:  {css}')
        return False


def click_by_actionchains(selector, sleep=2):
    publish = g_driver.find_element_by_css_selector(selector)
    try:
        ActionChains(g_driver).click(publish).perform()
    except TimeoutException as e:
        g_driver.logger.warning(f'get：{selector} {e}')
    time.sleep(sleep)
    g_driver.logger.info(f"点击 {selector} 按钮成功")
    return True


def click_select(clickCSS, selectCSS, para):
    if para:
        if click(clickCSS):
            if single_select(selectCSS, para):
                return True
        else:
            logger.info(f'click_select:参数：{para} 无法赋值，没有找到定位 {clickCSS}')
            return False
    logger.info(f'click_select:定位 {clickCSS} 没有参数')
    return False


def single_select(css, para, trim_price=False):
    if para:
        try:
            eles = g_driver.find_elements(By.CSS_SELECTOR, css)
            for e in eles:
                para_text = para.replace(" ", "")
                ele_text = e.text.replace(" ", "")
                if trim_price:
                    ele_text = ele_text.split('\n')[0]
                if ele_text == para_text:
                    logger.info(para)
                    e.click()
                    return True
        except Exception as e:
            warnStr = f'single_select: 定位:{css}  参数: {para} 错误信息: {e} '
            logger.info(warnStr)
    logger.info(f'single_select:定位 {css} 没有参数')
    return False


def get_sorted_imgs(dir_name):
    """
    根据文件夹地址返回这个文件夹下所有图片,按照数字顺序返回
    eg.
    ['1_01.jpg',
     '1_02.jpg',
     '1_03.jpg',
     '1_04.jpg',
     '1_05.jpg',
     '2.jpg',
     '3_01.jpg',
     '3_02.jpg',
     '3_03.jpg',
     '3_04.jpg',
     '3_05.jpg',
     '3_06.jpg',
     '4_01.jpg',
     '4_02.jpg']
    :param dir_name: 文件夹地址
    :return:
    """
    l = os.listdir(dir_name)
    return sorted(l, key=lambda x: x[:-4])


def clear_and_send_keys(css, value):
    ele = g_driver.find_element_by_css_selector(css)
    ele.clear()
    ele.send_keys(value)
