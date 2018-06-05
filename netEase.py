import time
from datetime import datetime

import logzero
from logzero import logger
from selenium.webdriver.support.ui import Select

from config import LOGFILE_NAME, DATA_CHAPTER_IMAGE, DATA_WORKS_NAME, DATA_CHAPTER_NAME, DATA_PASSWORD, \
    DATA_USERNAME, DATA_IS_CLOCK, DATA_CLOCK_PUBLISH_DATETIME, DATA_LOGIN_TYPE, PLATFORM_STATUS_AUTH_FAIL, \
    PLATFORM_STATUS_AUTH_OK, DATA_PLATFORM, CAPTCHAR_PATH
from data import data
from utils import open_driver, get, track_alert, get_current_url, g_mysqlid, Pang5Exception, update_login_status
from captcha_utils import image_recog

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
MANAGE_URL = 'https://zz.manhua.163.com/'
COOKIE_DOMAIN = ".manhua.163.com"


# COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{login_username}.cookie.pkl'


class Upload:
    def __init__(self):
        logger.info(data)

    def process(self, mysql_id):
        g_mysqlid["mysql_id"] = mysql_id
        with open_driver(phone_ua=True, browser='firefox') as driver:
            with track_alert(driver):
                # 处理登录
                login_username = data[DATA_USERNAME]
                login_password = data[DATA_PASSWORD]
                logger.info(f'用户名{login_username}')
                logger.info(f'密码{login_password}')

                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if data[DATA_LOGIN_TYPE] == 'mobile':
                        self.mobile_login(driver, login_username, login_password)
                    elif data[DATA_LOGIN_TYPE] in ('mail', '', 'email'):
                        self.mail_login(driver, login_username, login_password)
                    elif data[DATA_LOGIN_TYPE] == 'qq':
                        self.qq_login(driver, login_username, login_password)
                    elif data[DATA_LOGIN_TYPE] == 'weibo':
                        self.weibo_login(driver)
                    elif data[DATA_LOGIN_TYPE] == 'weixin':
                        self.weixin_login(driver)
                    else:
                        raise Pang5Exception('暂时不支持您的登录方式')
                    # self.mobile_login(driver)

                    # 登录
                    # 继续中间页面
                    get('https://zz.manhua.163.com/')
                    time.sleep(3)
                if get_current_url() not in ['http://zz.manhua.163.com/', 'https://zz.manhua.163.com/']:
                    status = PLATFORM_STATUS_AUTH_FAIL
                    update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                        platform_password=data[DATA_PASSWORD], platform_status=status)
                    raise Pang5Exception('登录失败')
                time.sleep(1)
                logger.info('登录成功')
                status = PLATFORM_STATUS_AUTH_OK
                update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                    platform_password=data[DATA_PASSWORD], platform_status=status)
                # try:
                net_series = driver.find_elements_by_link_text(data[DATA_WORKS_NAME])
                if len(net_series) == 0:
                    raise Pang5Exception("该用户下没有该作品")
                net_series[0].click()
                time.sleep(1)
                handles = driver.window_handles
                time.sleep(1)
                driver.switch_to_window(handles[-1])
                js = "window.scrollTo(0, document.body.scrollHeight)"
                driver.execute_script(js)
                driver.find_element_by_css_selector('#panel1 > div > div > a').click()
                self.form(driver)
                # except:
                #     logger.error('error')

    # 邮箱登录
    def mail_login(self, driver, login_username, login_password) -> bool:
        logger.info('用邮箱登录')
        if '@' not in login_username:
            status = PLATFORM_STATUS_AUTH_FAIL
            update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                platform_password=data[DATA_PASSWORD], platform_status=status)
            raise Pang5Exception('登录方式是邮箱,但是输入的用户名不是邮箱')
        get('https://manhua.163.com/')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        driver.find_element_by_css_selector('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required').click()
        # driver.find_element_by_css_selector('.sns-mobile').click()
        driver.switch_to.frame(driver.find_element_by_id("x-URS-iframe"))
        username = driver.find_element_by_name('email')
        username.clear()
        username.send_keys(login_username)
        password = driver.find_element_by_name('password')
        password.clear()
        password.send_keys(login_password)
        time.sleep(1)
        driver.find_element_by_id('dologin').click()
        time.sleep(2)
        return True

    # qq登录
    def qq_login(self, driver, login_username, login_password) -> bool:
        logger.info('用qq登录')
        get('https://manhua.163.com/')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        driver.find_element_by_css_selector('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required').click()
        time.sleep(3)
        driver.find_element_by_css_selector('#common_login > div.m-loginswitch > ul > li:nth-child(2) > a > i').click()
        time.sleep(3)
        print(get_current_url())
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        driver.switch_to_frame(driver.find_element_by_id("ptlogin_iframe"))
        driver.find_element_by_id('switcher_plogin').click()
        time.sleep(3)

        u = driver.find_element_by_id('u')
        u.clear()
        u.send_keys(login_username)
        p = driver.find_element_by_id('p')
        p.clear()
        p.send_keys(login_password)
        driver.find_element_by_id('login_button').click()
        time.sleep(3)

        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        return True

    # 微博登录

    def weibo_login(self, driver):
        logger.info('用微博登录')
        get(
            'https://h5.manhua.163.com/login/form?targetUrl=https%3A%2F%2Fh5.manhua.163.com%2Fsubscribe%3Fsigned_in_callback%3D1')
        driver.find_element_by_css_selector('#sina').click()
        time.sleep(3)
        # 一个字母一个字母的输入
        for i in list(data[DATA_USERNAME]):
            driver.find_element_by_css_selector('#userId').send_keys(i)
            time.sleep(0.5)
        time.sleep(2)
        for i in list(data[DATA_PASSWORD]):
            driver.find_element_by_css_selector('#passwd').send_keys(i)
            time.sleep(0.5)
        # js = f'document.getElementById("userId").setAttribute("value","{data[DATA_USERNAME]}");' \
        #      f'document.getElementById("passwd").setAttribute("value","{data[DATA_PASSWORD]}");'
        # driver.execute_script(js)
        # import pyautogui
        # pyautogui.press('f5')
        # time.sleep(2)
        # js = 'document.getElementById("userId").focus()'
        # driver.execute_script(js)
        # pyautogui.typewrite(data[DATA_USERNAME])
        # time.sleep(2)
        # pyautogui.keyDown('tab')
        # pyautogui.keyUp('tab')
        # pyautogui.typewrite(data[DATA_PASSWORD])
        # time.sleep(2)

        # 处理验证码问题
        captcha_div = driver.find_element_by_css_selector(
            'p.oauth_code:nth-child(3)')
        if captcha_div.is_displayed():
            logger.info('有验证码, 截图')
            captcha_img = captcha_div.find_element_by_css_selector('span img')
            store_path = f"{CAPTCHAR_PATH}/netEase_{datetime.now().strftime('%Y-%m-%d %H%M%S')}.png"
            captcha_img.screenshot(store_path)

            logger.info('调用服务识别')
            result, ok = image_recog(store_path)
            if ok:
                logger.info(f'识别成功,填写{result}')
                captcha_div.find_element_by_css_selector('input').send_keys(result)
            else:
                logger.error('验证码识别失败')

        driver.find_element_by_css_selector('a.WB_btn_login').click()
        # pyautogui.press('enter')
        time.sleep(3)

        return 'weibo' in get_current_url()

    # 微信登录
    def weixin_login(self, driver):
        raise Pang5Exception('暂时不支持微信登录')

    # 手机登录
    def mobile_login(self, driver, login_username, login_password) -> bool:

        logger.info('用手机号登录')
        get('https://manhua.163.com/')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        driver.find_element_by_css_selector('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required').click()
        time.sleep(3)
        driver.find_element_by_css_selector('.sns-mobile').click()
        # click('.sns-mobile')
        username = driver.find_element_by_id('username')
        username.clear()
        username.send_keys(login_username)
        time.sleep(3)

        password = driver.find_element_by_id('password')
        password.clear()
        password.send_keys(login_password)
        time.sleep(3)

        driver.find_element_by_css_selector('form.login-classic > div:nth-child(8) > button').click()

        return True

    def form(self, driver):
        '''
                    表单处理部分
                    '''
        chapter_name = data[DATA_CHAPTER_NAME]
        chapter_img = data[DATA_CHAPTER_IMAGE]
        is_clock = data[DATA_IS_CLOCK]
        if is_clock:
            publish_day = data[DATA_CLOCK_PUBLISH_DATETIME].split(' ')[0]
            pubish_hour = data[DATA_CLOCK_PUBLISH_DATETIME].split(' ')[1].split(':')[0]
            min = int(data[DATA_CLOCK_PUBLISH_DATETIME].split(' ')[1].split(':')[1])
            if min < 15:
                publish_min = "00"
            elif min >= 15 and min < 30:
                publish_min = "15"
            elif min >= 30 and min < 45:
                publish_min = "30"
            elif min >= 45 and min < 60:
                publish_min = "45"
        # input处理readonly
        js = "$('input').removeAttr('readonly')"
        time.sleep(1)
        title = driver.find_element_by_id('title')

        # 正文
        title.send_keys(chapter_name)
        time.sleep(1)
        # 提示上传
        # 上传多个文件
        logger.info('共有图片%d张' % len(chapter_img))
        for i, f in enumerate(chapter_img):
            file = driver.find_element_by_css_selector('.webuploader-element-invisible')
            file.send_keys(f)
            div = driver.find_element_by_css_selector('div.episode-upload-throbber')
            while div.is_displayed():
                percent = div.find_element_by_css_selector('div>span').text
                logger.info(f'图片{i}, 上传进度 {percent}')
                time.sleep(1)
            logger.info('上传完成')

        driver.execute_script(js)
        # 定时
        if is_clock:
            driver.find_element_by_id('timing_flag').click()

            autoPublishDate = driver.find_element_by_css_selector(
                '#timing > div > div.small-4.columns > input[type="text"]')
            autoPublishDate.clear()
            # 日期
            autoPublishDate.send_keys(publish_day)
            h = Select(driver.find_element_by_css_selector('#timing > div > div:nth-child(2) > select'))
            # 小时
            h.select_by_visible_text(pubish_hour)
            m = Select(driver.find_element_by_css_selector('#timing > div > div:nth-child(4) > select'))
            # 分钟
            m.select_by_visible_text(publish_min)
        # 提交
        time.sleep(2)
        # 干掉小女生的遮挡
        driver.execute_script('$("#j-epay-warning").remove();')
        driver.find_element_by_xpath('/html/body/section[1]/div/div[3]/div/form/div[5]/div[2]/button[2]').click()
        errs = driver.find_elements_by_css_selector('#firstModal > div.reveal-modal-body.default > div:nth-child(1)')
        if len(errs) > 0:
            raise Pang5Exception(errs[0].text)
        time.sleep(3)
        logger.info('发布成功')


def main(mysql_id):
    Upload().process(mysql_id)


if __name__ == '__main__':
    # Upload_netEase = Upload()
    # Upload_netEase.main()
    main(10000)
