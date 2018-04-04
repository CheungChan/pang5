from utils import open_driver, track_alert, get, click, store_cookie, add_cookie, get_current_url, get_sorted_imgs
import time
from selenium.webdriver.support.ui import Select
import os
from logzero import logger
from data import data

MANAGE_URL = 'https://zz.manhua.163.com/'
COOKIE_DOMAIN = ".manhua.163.com"
login_username = data['net_username']
login_password = data['net_password']
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{login_username}.cookie.json'
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
                    if data['net-login']=='mobile':
                        self.mobile_login(driver, login_username, login_password)
                    elif data['net-login']=='mail':
                        self.mail_login(driver, login_username, login_password)
                    # self.mobile_login(driver)

                    store_cookie(driver, COOKIE_FILE)
                    logger.info('登录成功')
                    # 登录
                    # 继续中间页面
                    get('http://zz.manhua.163.com/')
                time.sleep(1)
                # try:
                driver.find_element_by_link_text(data['net_series_title']).click()
                print(1)
                time.sleep(1)
                handles = driver.window_handles
                time.sleep(1)
                driver.switch_to_window(handles[-1])
                js = "window.scrollTo(0, document.body.scrollHeight)"
                driver.execute_script(js)
                driver.find_element_by_css_selector('#panel1 > div > div > a').click()
                print(2)

                self.form(driver, data['net_title_text'], data['net_image_pic'], data['net_d'], data['net_h'],
                          data['net_m'], data['net-use-appoint'])
                # except:
                #     logger.error('error')


    # 邮箱登录
    def mail_login(self, driver, login_username, login_password):
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
        pass

    # qq登录
    def qq_login(self, driver):
        pass

    # 微博登录

    def weibo_login(self, driver):
        pass

    # 微信登录
    def weixin_login(self, driver):
        logger.error('不支持微信')
        return

    # 手机登录
    def mobile_login(self, driver, login_username, login_password):

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
        title = driver.find_element_by_id('title')
        # 正文
        title.send_keys(title_text)
        time.sleep(1)
        # 提示上传
        # 上传多个文件
        for i in dir_name:
            file = driver.find_element_by_css_selector('.webuploader-element-invisible')
            file.send_keys(i)

            self.stop(driver)

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
        # 判断是不是上传完成
        self.stop(driver)
        # 提交
        time.sleep(2)
        driver.find_element_by_xpath('/html/body/section[1]/div/div[3]/div/form/div[5]/div[2]/button[2]').click()

    # 看是否上传完
    def stop(self, driver):
        phui_backdrop = driver.find_element_by_class_name('phui-backdrop')
        while phui_backdrop.is_displayed():
            logger.info('暂停,文件未上传完成')
            time.sleep(0.5)

def main():
    Upload().main()


if __name__ == '__main__':
    # Upload_netEase = Upload()
    # Upload_netEase.main()
    main()