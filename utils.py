import json
import os
import pickle
import random
import string
import time
import traceback
from datetime import datetime

import logzero
import oss2
import records
from logzero import logger
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException, WebDriverException, \
    SessionNotCreatedException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait, Select

from config import USE_FACE, CHROME_DRIVER_PATH, PHANTOMJS_PATH, SCREENSHOT_PATH, WAIT_CLICKABLE, WAIT_PRESENCE, \
    WAIT_VISIABLITY, CHROME_ARG, FIREFOX_DRIVER_PATH, RUN_SIKULIX_CMD, LOGFILE_NAME, MYSQL_URL, DATA_PASSWORD, DEBUG, \
    DATA_PLATFORM
from dingding_qun import dingdSendMsg, dingSendMarkdown

g_driver = None
g_mysqlid = {"mysql_id": None}
g_msg = ''
g_traceback = ''
g_screenshot = ''
# 此变量要在平台的脚本中修改值,所有采用了dict的结构,为可变对象,才能修改.平台脚本必须修改该值.
logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)


class open_driver(object):
    def __init__(self, width=1920, height=7000, cookie_domain=None, load_image=False, cookie_file=None,
                 browser='chrome', phone_ua=False):
        self.width = width
        self.height = height
        self.cookie_domain = cookie_domain
        self.load_image = load_image
        if self.cookie_domain:
            self.cookie_file = cookie_file
        self.browser = browser
        self.phone_ua = phone_ua

    def __enter__(self):
        global g_driver
        if USE_FACE:
            if self.browser == 'chrome':
                option = webdriver.ChromeOptions()
                for iarg in CHROME_ARG:
                    option.add_argument(iarg)
                if self.phone_ua:
                    UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
                    option.add_argument(f'user-agent={UA}')
                prefs = {
                    "profile.default_content_setting_values.plugins": 1,
                    "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
                    "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
                    "profile.default_content_setting_values": {
                        "notifications": 2
                    }
                }
                option.add_experimental_option("prefs", prefs)
                self.driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=option)

                logger.info('chrome浏览器打开')
                self.driver.get('http://www.baidu.com')
            elif self.browser == 'firefox':
                profile = webdriver.FirefoxProfile()
                profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'true')
                profile.set_preference("plugin.state.flash", 2)
                self.driver = webdriver.Firefox(executable_path=FIREFOX_DRIVER_PATH, firefox_profile=profile)

                logger.info('firefox浏览器打开')
                # self.driver.get('http://www.baidu.com')

            self.driver.maximize_window()

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
        # self.driver.set_window_size(self.width, self.height)
        js = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.scroll_buttom = lambda: self.driver.execute_script(js)
        g_driver = self.driver
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        global g_traceback
        global g_msg
        global g_screenshot
        logger.info('退出')
        if exc_type == SessionNotCreatedException or exc_type == NoSuchWindowException:
            g_msg = "浏览器找不到了"
            update_status2fail()
            return True
        if exc_tb:
            try:
                g_screenshot = f"{SCREENSHOT_PATH}/excep_{datetime.now().strftime('%Y-%m-%d %H%M%S')}.png"
                self.driver.get_screenshot_as_file(g_screenshot)
            except WebDriverException:
                g_msg = '截图失败,浏览器找不到了'
                g_screenshot = ''
                update_status2fail()
                return True
        logger.info('屏蔽关闭提示框')
        self.driver.execute_script("window.onbeforeunload = function(e){};")
        logger.info("浏览器关闭")
        # quit是关闭所有窗口  close是关闭当前窗口
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass
        if exc_tb:
            logger.error("出现异常")
            logger.error(exc_type)
            logger.error(exc_val)
            logger.error(exc_tb)
            g_traceback = traceback.format_exc()
            logger.error(g_traceback)
            if exc_type != Pang5Exception:
                g_msg = ("出现异常,浏览器只能关闭")
            update_status2fail()
            return True
        else:
            update_status2OK()
        return True


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


class Pang5Exception(Exception):
    def __init__(self, msg):
        global g_msg
        g_msg = msg


def update_status2fail():
    db = records.Database(MYSQL_URL)
    rows = db.query("update chapter_chapter set status=-1, fail_reason=:msg where id=:id", id=g_mysqlid['mysql_id'],
                    msg=g_msg)

    # 发送钉钉群
    env = '测试环境' if DEBUG else '生产环境'
    from data import data
    data.update({DATA_PASSWORD: "*******"})

    if g_screenshot:

        # 将截图上传到网络
        IMG_URL = 'http://pang5web.oss-cn-beijing.aliyuncs.com/'
        file_name = set_file_name()
        image_name = 'pang5web/error/' + file_name + '.png'
        put_object_from_file(g_screenshot, image_name, 'pang5web')
        screen_url = IMG_URL + image_name

        # 发送markdown
        title = f'{env}: 漫画助手发布失败'
        markdown = f"""
# platform={data[DATA_PLATFORM]}\n\n
# mysql_id={g_mysqlid["mysql_id"]}\n\n
# msg={g_msg}\n\n
- data={data}\n\n
- traceback={g_traceback}\n\n
# 以下是截图
![screenshot]({screen_url})\n\n
        """
        logger.info(title)
        logger.info(markdown)
        dingSendMarkdown(title, markdown)
    else:
        # 发送text
        dingding_s = f'{env}: 漫画助手发布失败\n\n' \
                     f'platform={data[DATA_PLATFORM]}\n\n' \
                     f'mysql_id={g_mysqlid["mysql_id"]}\n\n' \
                     f'msg={g_msg}\n\n' \
                     f'data={data}\n\n' \
                     f'traceback={g_traceback}\n\n' \
                     f'没有截图'
        logger.error(dingding_s)
        dingdSendMsg(dingding_s)

    logger.info(f'{env}: 更新{g_mysqlid["mysql_id"]}状态')


def update_status2OK():
    # 没有异常, 更改数据库状态
    db = records.Database(MYSQL_URL)
    rows = db.query('update chapter_chapter set status=0, ok_time=:ok_time where id=:id', id=g_mysqlid["mysql_id"],
                    ok_time=datetime.now())
    env = '测试环境' if DEBUG else '生产环境'
    logger.info(f'{env}: 更新{g_mysqlid["mysql_id"]}状态')


def update_login_status(platform, platform_username, platform_password, platform_status):
    """
    更改登录的账号状态, 0待校验 1 校验通过 2 校验失败
    :param platform:
    :param platform_username:
    :param password:
    :return:
    """
    db = records.Database(MYSQL_URL)
    rows = db.query("update subscriber_platformsubscriber set platform_status=:platform_status where "
                    "platform=:platform and "
                    "platform_username=:platform_username and "
                    "platform_password=:platform_password", platform_status=platform_status, platform=platform,
                    platform_username=platform_username, platform_password=platform_password)
    env = '测试环境' if DEBUG else '生产环境'
    logger.info(f'{env}: 更改账号状态,{locals()}')


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
    cookies = pickle.load(open(cookie_file, 'rb'))
    for c in cookies:
        if c.get('domain') != cookie_domain:
            continue
        driver.add_cookie(c)
    logger.info('加载完成')
    return True


def store_cookie(driver, cookie_file):
    logger.info('存储cookie')
    new_cookies = driver.get_cookies()
    pickle.dump(new_cookies, open(cookie_file, 'wb'))
    logger.info('加载完成')


def get(url, sleep=2):
    try:
        logger.info(f'get:{url}')
        g_driver.implicitly_wait(10)
        # Firefox的bug, 如果不调用switch_to.default_content()会报错cannt access dead object
        g_driver.switch_to.default_content()
        g_driver.get(url)
    except TimeoutException as e:
        g_driver.logger.warning(f'get: {url} {e}')
        try:
            refresh_recursion(url)
        except TimeoutException as e2:
            return True
        time.sleep(sleep)
    except Exception as e:
        logger.error(e)
        return False
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
        logger.info(f'get：{selector} {e}')
    time.sleep(sleep)
    logger.info(f"点击 {selector} 按钮成功")
    return True


def click_by_pyautogui(image_path):
    """
    根据pyautogui提供的图像识别技术，点击屏幕上的像素点
    :return:
    """
    USE_CACHE = True
    MAX_RETRY_TIMES = 2
    retry_times = MAX_RETRY_TIMES
    import pyautogui
    width, height = pyautogui.size()
    if not os.path.isabs(image_path):
        # 适配不同分辨率的图片， 仿大安卓
        image_path = os.path.join(os.path.abspath('.'), 'upload_btn_images', f'{width}_{height}', image_path)
    assert os.path.exists(image_path), logger.error(f'{image_path}文件不存在')
    cache_loc_files = f'{image_path}.loc.txt'
    while retry_times > 0:
        # 如果可以用缓存位置的话
        can_use_cache_loc = USE_CACHE and retry_times == MAX_RETRY_TIMES and os.path.exists(cache_loc_files)
        if can_use_cache_loc:
            with open(cache_loc_files, 'r', encoding='utf-8') as f:
                s = f.read().split(',')
                loc = int(s[0]), int(s[1])
                logger.info(f'使用缓存位置{loc}')
        else:
            # 如果不能用缓存的话
            loc = pyautogui.locateCenterOnScreen(image_path)
        if loc:
            x, y = loc
            logger.info(f'x={x}, y={y}')
            pyautogui.moveTo(x, y)
            pyautogui.click(x, y)
            time.sleep(2)
            if USE_CACHE:
                # 缓存到文件中
                with open(cache_loc_files, 'w', encoding='utf-8') as f:
                    f.write(f'{x},{y}')
                    logger.info(f'存储缓存位置{x,y}')
            break
        else:
            retry_times -= 1
            if retry_times > 0:
                logger.info(f'重试{retry_times}')
                time.sleep(1)
            else:
                logger.error(f'{image_path} 在页面上不能找到')
                raise Pang5Exception('发布失败,会在稍后重试')


def click_by_sikulix(image_path):
    """
    使用sikulix根据按钮图片点击按钮
    :param image_path: 按钮图片路径  可以传绝对路径 也可以传递相对路径 相对路径是相对D:/PycharmWorkspace/pang5/upload_btn_images
    :return:
    """
    if not os.path.isabs(image_path):
        image_path = os.path.join(os.path.abspath('.'), 'upload_btn_images', image_path)
    skl = os.path.join(os.path.abspath('.'), 'upload_image.skl')
    cmd = f'{RUN_SIKULIX_CMD} -r {skl} --args {image_path}'
    logger.info(cmd)
    os.system(cmd)


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
    ['1.jpg',
     '02.jpg',
     '03.jpg',
     '04.jpg',
     '05.jpg',
     ]
    :param dir_name: 文件夹地址
    :return:
    """
    l = os.listdir(dir_name)
    l = list(filter(lambda x: not x.startswith('.'), l))
    return sorted(l, key=lambda x: int(x.find('.')))


def clear_and_send_keys(css, value):
    ele = g_driver.find_element_by_css_selector(css)
    ele.clear()
    ele.send_keys(value)


def select_value(css, value):
    s = Select(g_driver.find_element_by_css_selector(css))
    s.select_by_value(value)


def use_flash():
    # POSITION_PERMISSION = (216, 93)
    POSITION_PERMISSION = (109, 48)
    # POSITION_FLASH = (720, 400)
    POSITION_FLASH = (360, 200)
    import pyautogui as pg

    pg.click(*POSITION_PERMISSION)
    time.sleep(1)
    pg.click(*POSITION_FLASH)
    time.sleep(1)

    pg.press(['down', 'down'])
    pg.keyDown('enter')
    pg.keyUp('enter')
    pg.keyDown('escape')
    pg.keyUp('escape')
    pg.keyDown('f5')
    pg.keyUp('f5')


def scroll_to(height="document.body.scrollHeight"):
    js = f"window.scrollTo(0, {height})"
    g_driver.execute_script(js)


def scroll_to_id(id):
    js = f'location.href="#{id}"'
    g_driver.execute_script(js)


auth = oss2.Auth('LTAI0OrY1GUzZxD2', 'G9lgeS1ogDUl1ex6N2pHsmqlmqNGIX')


def put_object_from_file(file, file_name, bucket):
    endpoint = 'http://pang5web.oss-cn-beijing.aliyuncs.com/'  # 假设你的Bucket处于杭州区域
    bucket = oss2.Bucket(auth, endpoint, bucket, is_cname=True, enable_crc=False)
    bucket.put_object_from_file(file_name, file)


def set_file_name():
    file_name = time.strftime("%Y%m%d%H%M%S", time.localtime()) + '_' + ''.join(
        random.sample(string.ascii_letters + string.digits, 8))

    return file_name
