from utils import open_driver, track_alert, get, click, store_cookie, add_cookie, get_current_url
import time
from selenium.webdriver.support.ui import Select
import os
from logzero import logger

MANAGE_URL = 'https://zz.manhua.163.com/'
COOKIE_DOMAIN = ".manhua.163.com"
USERNAME = '18101038354'
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{USERNAME}.cookie.json'
from selenium.webdriver.support.ui import WebDriverWait


class Upload:
    def __init__(self):
        logger.info('开始')

    def main(self):
        with open_driver(cookie_domain=".manhua.163.com",
                         cookie_file=COOKIE_FILE) as driver:
            with track_alert(driver):
                # 处理登录
                add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    self.mail_login(driver)
                    # self.mobile_login(driver)
                    store_cookie(driver, COOKIE_FILE)
                    logger.info('登录成功')
                    # 登录
                    # 继续中间页面
                    get('http://zz.manhua.163.com/')
                time.sleep(1)
                driver.find_element_by_link_text('为什么救赎').click()
                time.sleep(1)
                driver.find_element_by_link_text('新增话').click()
                self.form(driver)
    #邮箱登录
    def mail_login(self, driver,login_username='18101038354',login_password='qingdian'):
        get('https://manhua.163.com/')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        driver.find_element_by_css_selector('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required').click()
        # driver.find_element_by_css_selector('.sns-mobile').click()
        time.sleep(1)
        username = driver.find_elements_by_name('email')
        pr
        username.clear()
        username.send_keys(login_username)
        password = driver.find_element_by_name('password')
        password.clear()
        password.send_keys(login_password)
        driver.find_element_by_css_selector('form.login-classic > div:nth-child(8) > button').click()
        pass
    #qq登录
    def qq_login(self,driver):
        pass
    #微博登录

    def weibo_login(self,driver):
        pass
    #微信登录
    def weixin_login(self,driver):
        logger.error('不支持微信')
        return
    #手机登录
    def mobile_login(self, driver,login_username='18101038354',login_password='qingdian'):

        get('https://manhua.163.com/')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        driver.find_element_by_css_selector('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required').click()

        # driver.find_element_by_css_selector('.sns-mobile').click()
        click('.sns-mobile')
        time.sleep(1)
        username = driver.find_element_by_id('username')
        username.clear()
        username.send_keys(login_username)
        password = driver.find_element_by_id('password')
        password.clear()
        password.send_keys(login_password)
        driver.find_element_by_css_selector('form.login-classic > div:nth-child(8) > button').click()

        return driver

    def form(self, driver, title_text='胖5号', dir_name=os.getcwd() + '/pic', d='2019-01-01', h_num='23', m_num='15'):
        '''
                    表单处理部分
                    '''
        # input处理readonly
        js = "$('input').removeAttr('readonly')"
        time.sleep(1)
        title = driver.find_element_by_id('title')
        # 正文
        title.send_keys(title_text)
        time.sleep(1)
        # 提示上传
        # 上传多个文件
        for i in sorted(os.listdir(dir_name)):
            file = driver.find_element_by_css_selector('.webuploader-element-invisible')
            file.send_keys(dir_name + '/' + i)
            self.stop(driver)

        driver.execute_script(js)
        # 定时
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
        # 判断是不是上传完成
        self.stop(driver)
        # 提交
        driver.find_element_by_css_selector(
            'body > section:nth-child(2) > div > div.large-9.medium-8.columns > div > form > div:nth-child(9) > div.small-10.columns > button.small.btn-normal.right').click()

    # 看是否上传完
    def stop(self, driver):
        phui_backdrop = driver.find_element_by_class_name('phui-backdrop')
        while phui_backdrop.is_displayed():
            logger.info('暂停,文件未上传完成')
            time.sleep(0.5)
if __name__ == '__main__':
    # Upload_netEase = Upload()
    # Upload_netEase.main()
    Upload().main()
