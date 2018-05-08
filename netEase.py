import time

from logzero import logger
from selenium.webdriver.support.ui import Select

from data import data
import logzero
from config import LOGFILE_NAME
from utils import open_driver, get, track_alert, add_cookie, get_current_url, store_cookie, g_mysqlid, Pang5Exception

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
MANAGE_URL = 'https://zz.manhua.163.com/'
COOKIE_DOMAIN = ".manhua.163.com"

# COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{login_username}.cookie.pkl'


class Upload:
    def __init__(self):
        logger.info(data)

    def process(self, mysql_id):
        g_mysqlid["mysql_id"] = mysql_id
        with open_driver() as driver:
            with track_alert(driver):
                # 处理登录
                # add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
                login_username = data['net_username']
                login_password = data['net_password']
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if data['net-login'] == 'mobile':
                        self.mobile_login(driver, login_username, login_password)
                    elif data['net-login'] in ('mail',''):
                        self.mail_login(driver, login_username, login_password)
                    elif data['net-login'] == 'qq':
                        self.qq_login(driver, login_username, login_password)
                    # self.mobile_login(driver)

                    # store_cookie(driver, COOKIE_FILE)
                    # 登录
                    # 继续中间页面
                    get('http://zz.manhua.163.com/')
                if get_current_url() !='http://zz.manhua.163.com/':
                    raise  Pang5Exception('登录失败')
                time.sleep(1)
                logger.info('登录成功')
                # try:
                net_series = driver.find_elements_by_link_text(data['net_series_title'])
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
                self.form(driver, data['net_title_text'], data['net_image_pic'], data['net_d'], data['net_h'],
                          data['net_m'], data['net-use-appoint'])
                # except:
                #     logger.error('error')

    # 邮箱登录
    def mail_login(self, driver, login_username, login_password):
        logger.info('用邮箱登录')
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

    # qq登录
    def qq_login(self, driver, login_username, login_password):
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

    # 微博登录

    def weibo_login(self, driver):
        raise Pang5Exception('暂时不支持微博登录')

    # 微信登录
    def weixin_login(self, driver):
        raise Pang5Exception('不支持微信')

    # 手机登录
    def mobile_login(self, driver, login_username, login_password):

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

        return driver

    def form(self, driver, title_text, dir_name, d, h_num, m_num, net_use_appoint):
        '''
                    表单处理部分
                    '''
        # input处理readonly
        js = "$('input').removeAttr('readonly')"
        time.sleep(1)
        title = driver.find_elements_by_id('title')

        # 正文
        title.send_keys(title_text)
        time.sleep(1)
        # 提示上传
        # 上传多个文件
        logger.info('共有图片%d张' % len(dir_name))
        for i, f in enumerate(dir_name):
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
        if net_use_appoint:
            driver.find_element_by_id('timing_flag').click()

            autoPublishDate = driver.find_element_by_css_selector(
                '#timing > div > div.small-4.columns > input[type="text"]')
            autoPublishDate.clear()
            # 日期
            autoPublishDate.send_keys(d)
            h = Select(driver.find_element_by_css_selector('#timing > div > div:nth-child(2) > select'))
            # 小时
            h.select_by_value(h_num)
            m = Select(driver.find_element_by_css_selector('#timing > div > div:nth-child(4) > select'))
            # 分钟
            m.select_by_value(m_num)
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
