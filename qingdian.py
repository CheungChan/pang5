import os
import time

from logzero import logger

from utils import open_driver, track_alert, get, store_cookie

MANAGE_URL = 'http://page.qingdian.cn/center/comicManagement/upload'
LOGIN_URL = 'http://page.qingdian.cn/passport/login'

COOKIE_DOMAIN = ".qingdian.cn"
LOGIN_USERNAME = '13311095487'
LONGIN_PASSWORD = '12345'
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{LOGIN_USERNAME}.cookie.json'


class Upload:
    def __init__(self):
        logger.info('开始')
        self.driver = None

    def main(self):
        with open_driver(cookie_domain=COOKIE_DOMAIN,
                         cookie_file=COOKIE_FILE) as driver:
            self.driver = driver
            with track_alert(driver):
                self.mobile_login(driver)
                store_cookie(driver, COOKIE_FILE)
                get(MANAGE_URL)
                self.driver.find_element_by_link_text('我的作品').click()
                self.search_article('今天天气很好')
                self.form(driver)
                time.sleep(100)

    # 手机登录
    def mobile_login(self, driver, login_username='13311095487', login_password='123456'):

        get('http://page.qingdian.cn/passport/login')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        # click('.sns-mobile')
        username = driver.find_element_by_css_selector(
            '#app > div:nth-child(1) > div.clearfix.ui-area.passport-content > div.passport-right > div > div > div.pic-box > div.qd-input-box.mb20 > div.qd-input > input[type="text"]')
        username.clear()
        username.send_keys(login_username)
        password = driver.find_element_by_css_selector(
            '#app > div:nth-child(1) > div.clearfix.ui-area.passport-content > div.passport-right > div > div > div.pic-box > div.qd-input.mb20 > input[type="password"]')
        password.clear()
        password.send_keys(login_password)
        driver.find_element_by_css_selector(
            '#app > div:nth-child(1) > div.clearfix.ui-area.passport-content > div.passport-right > div > div > div.pic-box > span').click()
        return driver

    def form(self, driver, title_text='胖5号', dir_name=os.getcwd() + '/pic', d='2019-01-01', h_num='23', m_num='15'):
        '''
                    表单处理部分
                    '''
        # input处理readonly
        js = "document.getElementsByTagName(\"input\").readOnly=false"
        time.sleep(1)
        title = driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div:nth-child(2) > div.mw-right > div.qd-input-box.mw-comic-name > div.qd-input > input[type="text"]')
        # 正文
        title.send_keys(title_text)
        time.sleep(1)
        # 提示上传
        # 上传多个文件
        for i in sorted(os.listdir(dir_name)):
            file = driver.find_element_by_css_selector('#add-section-img > div:nth-child(2) > input')
            file.send_keys(dir_name + '/' + i)
        driver.execute_script(js)
        # 定时
        driver.find_element_by_css_selector('.show-dialog').click()
        file = driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.cut-image-dialog.dialog-content > div > div.dialog-middle.clearfix > div.dm-btn-box.clearfix > div > input[type="file"]')
        file.send_keys(dir_name + '/' + '1.jpg')
        for i in range(20):
            driver.find_element_by_css_selector('.minus-btn').click()
        driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.cut-image-dialog.dialog-content > div > div.dialog-bottom > span.btn-theme.db-save').click()
        time.sleep(2)
        # 提交
        driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.mw-btn-box > span.btn-theme.btn-submit').click()

        time.sleep(200)

    def search_article(self, article_name):
        article_list = self.driver.find_elements_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(1) > div > ul > li')
        for a in article_list:
            print(a.find_element_by_css_selector('.mi-name-box').text)
            if "漫画名称：" + article_name == a.find_element_by_css_selector('.mi-name-box').text:
                a.find_element_by_css_selector(
                    '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(1) > div > ul > li:nth-child(1) > div > div.bottom-btn-box > div:nth-child(1) > span:nth-child(3)').click()
                return
        self.driver.find_element_by_css_selector('.btn-next').click()
        self.search_article(article_name)

    # 看是否上传完
    def stop(self, driver):
        phui_backdrop = driver.find_element_by_class_name('phui-backdrop')
        while phui_backdrop.is_displayed():
            logger.info('暂停,文件未上传完成')
            time.sleep(0.5)


if __name__ == '__main__':
    Upload().main()
