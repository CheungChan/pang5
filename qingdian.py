import time

import logzero
from logzero import logger

from config import LOGFILE_NAME, DATA_CHAPTER_IMAGE, \
    DATA_CHAPTER_NAME, DATA_WORKS_NAME, DATA_PASSWORD, DATA_USERNAME, DATA_WORKS_IMAGE, PLATFORM_STATUS_AUTH_OK, \
    PLATFORM_STATUS_AUTH_FAIL, DATA_PLATFORM
from data import data
from utils import open_driver, track_alert, get, g_mysqlid, get_current_url, Pang5Exception, update_login_status

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
MANAGE_URL = 'http://page.qingdian.cn/center/comicManagement/upload'
LOGIN_URL = 'http://page.qingdian.cn/passport/login'

COOKIE_DOMAIN = ".qingdian.cn"


class Qingdian:
    def __init__(self):
        logger.info(data)
        self.driver = None

    def process(self, mysql_id):
        g_mysqlid["mysql_id"] = mysql_id
        with open_driver() as driver:
            self.driver = driver
            with track_alert(driver):
                LOGIN_USERNAME = data[DATA_USERNAME]
                LOGIN_PASSWORD = data[DATA_PASSWORD]
                logger.info(f'用户名{LOGIN_USERNAME}')
                logger.info(f'密码{LOGIN_PASSWORD}')
                # 处理登录
                if not self.mobile_login(driver, LOGIN_USERNAME, LOGIN_PASSWORD):
                    status = PLATFORM_STATUS_AUTH_FAIL
                    update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                        platform_password=data[DATA_PASSWORD], platform_status=status)
                    raise Pang5Exception('登录失败')
                get(MANAGE_URL)
                time.sleep(2)
                cur = get_current_url()
                if cur != MANAGE_URL:
                    logger.error(MANAGE_URL)
                    status = PLATFORM_STATUS_AUTH_FAIL
                    update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                        platform_password=data[DATA_PASSWORD], platform_status=status)
                    raise Pang5Exception("登录失败")
                logger.info('登录成功')
                status = PLATFORM_STATUS_AUTH_OK
                update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                    platform_password=data[DATA_PASSWORD], platform_status=status)
                self.driver.find_element_by_link_text('我的作品').click()
                self.search_article(data[DATA_WORKS_NAME])
                self.form(driver)

    # 手机登录

    def mobile_login(self, driver, login_username, login_password) -> bool:

        get('http://page.qingdian.cn/passport/login')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        # click('.sns-mobile')
        username = driver.find_element_by_css_selector(
            '#app > div:nth-child(1) > div.clearfix.ui-area.passport-content > div.passport-right > div > div > div.pic-box > div.qd-input-box.mb20 > div.qd-input > input[type="text"]')
        username.clear()
        username.send_keys(login_username)
        time.sleep(2)
        password = driver.find_element_by_css_selector(
            '#app > div:nth-child(1) > div.clearfix.ui-area.passport-content > div.passport-right > div > div > div.pic-box > div.qd-input.mb20 > input[type="password"]')
        password.clear()
        password.send_keys(login_password)
        time.sleep(2)
        driver.find_element_by_css_selector(
            '#app > div:nth-child(1) > div.clearfix.ui-area.passport-content > div.passport-right > div > div > div.pic-box > span').click()
        return True

    def form(self, driver):
        '''
                    表单处理部分
                    '''
        chapter_name = data[DATA_CHAPTER_NAME]
        chapter_image = data[DATA_CHAPTER_IMAGE]
        works_image = data[DATA_WORKS_IMAGE]
        # input处理readonly
        js = "document.getElementsByTagName(\"input\").readOnly=false"
        time.sleep(1)
        title = driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div:nth-child(2) > div.mw-right > div.qd-input-box.mw-comic-name > div.qd-input > input[type="text"]')
        # 正文
        title.send_keys(chapter_name)
        time.sleep(1)
        # 提示上传
        # 上传多个文件

        for i in chapter_image:
            file = driver.find_element_by_css_selector('#add-section-img > div:nth-child(2) > input')
            logger.info('上传图片' + i)
            file.send_keys(i)

        driver.find_element_by_css_selector('.show-dialog').click()
        logger.info(f'上传封面图片{works_image}')
        file = driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.cut-image-dialog.dialog-content > div > div.dialog-middle.clearfix > div.dm-btn-box.clearfix > div > input[type="file"]')
        file.send_keys(works_image)
        # 判断图片预览是否存在
        css = "#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.cut-image-dialog.dialog-content > div > div.dialog-middle.clearfix > div:nth-child(1) > div.dm-cropper-box > img"
        nodisplay = 'display: none' in driver.find_element_by_css_selector(css).get_attribute('style')
        if nodisplay:
            raise Pang5Exception('封面图片不符合要求')
        for i in range(20):
            driver.find_element_by_css_selector('.minus-btn').click()
        driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.cut-image-dialog.dialog-content > div > div.dialog-bottom > span.btn-theme.db-save').click()
        time.sleep(2)
        self.stop(driver)
        # 提交
        driver.find_element_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(3) > div > div.mw-btn-box > span.btn-theme.btn-submit').click()
        time.sleep(2)
        # 捕获报错信息
        hint = driver.execute_script('return window.hint;')
        if hint:
            raise Pang5Exception(hint)
        logger.info('发布成功')

    def search_article(self, article_name):
        article_list = self.driver.find_elements_by_css_selector(
            '#app > div.center.shadow-bottom-line > div.center-main.ui-area > div.center-tab-content.clearfix > div.right-main > div > div > div:nth-child(1) > div > ul > li')
        for a in article_list:
            article_name_css = a.find_element_by_css_selector('.mi-name-box').text
            logger.info(article_name_css)
            if "漫画名称：" + article_name == article_name_css:
                logger.info(article_name_css)
                btns = a.find_elements_by_css_selector(
                    'div > div.bottom-btn-box > div:nth-child(1) > span:nth-child(3)')
                if len(btns) == 0:
                    raise Pang5Exception(f'作品"{article_name}"状态异常')
                else:
                    logger.info(f'找到{article_name}')
                    btns[0].click()
                    return
        btn = self.driver.find_element_by_css_selector('.btn-next')
        if 'disabled' not in btn.get_attribute('class'):
            logger.info('翻页')
            btn.click()
            time.sleep(1)
        else:
            raise Pang5Exception(f'用户没有绑定作品 "{article_name}"')
        self.search_article(article_name)

    # 看是否上传完
    def stop(self, driver):
        while True:

            # js得到对应的隐藏内容 bug......
            js = '''
            var a=true;
    document.querySelectorAll('div.upload-item >div.status-cover.status-uploading>span').forEach(function(val,index,arr){
    
     if(val.innerHTML != '100') a=false;
              
    });return a;
            '''
            stop = driver.execute_script(js)
            logger.info(stop)
            if stop:
                break
            else:
                time.sleep(2)


def main(mysql_id):
    Qingdian().process(mysql_id)


if __name__ == '__main__':
    main(10000)
    # main()
    # cookie=''
    # a=[{'domain': '.aliyun.com', 'expiry': 1537866231, 'httpOnly': False, 'name': 'isg', 'path': '/', 'secure': False, 'value': 'BElJpFuBd0S8zQsw8IjrIZ0WWHxjPjVHEHVXVOu-xTBvMmlEM-ZNmDdjcJGEatUA'}, {'domain': 'm.aliyun.com', 'httpOnly': True, 'name': 'maliyun_temporary_console0', 'path': '/', 'secure': False, 'value': '1AbLByOMHeZe3G41KYd5WfDVZM%2F%2BFx3TkBVLPaURYXEKCZfzWY99kPfj1fL7J7L6EnVDiUZjbpSJFkVya0sLmaVzELFHpRqD72xzZuu1AJIH1lJwMktZWc6GRho0%2BMg5d8hQih%2Fw7WYg1ZpfXyMC5Q%3D%3D'}, {'domain': '.aliyun.com', 'expiry': 1837674229, 'httpOnly': False, 'name': 'cna', 'path': '/', 'secure': False, 'value': '5ZlDEzwdBn0CAXx+sEWhx56B'}, {'domain': '.aliyun.com', 'expiry': 1524906229.68761, 'httpOnly': False, 'name': 'aliyun_lang', 'path': '/', 'secure': False, 'value': 'zh'}, {'domain': '.aliyun.com', 'expiry': 1837674229.687547, 'httpOnly': False, 'name': 'aliyun_site', 'path': '/', 'secure': False, 'value': 'CN'}, {'domain': '.aliyun.com', 'expiry': 1524906229.687481, 'httpOnly': False, 'name': 'aliyun_country', 'path': '/', 'secure': False, 'value': 'CN'}, {'domain': '.aliyun.com', 'httpOnly': True, 'name': 'hssid', 'path': '/', 'secure': False, 'value': '17doOeWLfX61c9oK7ZZzqbA1'}, {'domain': '.aliyun.com', 'httpOnly': True, 'name': 'login_aliyunid_csrf', 'path': '/', 'secure': False, 'value': '_csrf_tk_1253022314229628'}, {'domain': 'm.aliyun.com', 'httpOnly': True, 'name': 'JSESSIONID', 'path': '/', 'secure': False, 'value': 'B1666FC1-T4UTYCNOTL36Q0P3SR263-F96LACFJ-YZ52'}, {'domain': '.aliyun.com', 'expiry': 1837674232.160001, 'httpOnly': False, 'name': 'cnz', 'path': '/', 'secure': False, 'value': '95lDE078S2wCAUWwfnzBzdQN'}, {'domain': '.aliyun.com', 'httpOnly': True, 'name': 'hsite', 'path': '/', 'secure': False, 'value': '6'}, {'domain': '.aliyun.com', 'httpOnly': True, 'name': 'login_aliyunid_pk', 'path': '/', 'secure': False, 'value': '1246497347206613'}, {'domain': '.aliyun.com', 'httpOnly': True, 'name': 'login_aliyunid_ticket', 'path': '/', 'secure': False, 'value': 'xmc8vVl3h5bQu*lSQ2l0HvqodDA_sVpof_BNTwUhTOoNC1ZBeeMfKJzxdnb95hYssNIZor6q7SCxRtgmGCbifG2Cd4ZWazmBdHI6sgXZqg4XFWQfyKpeu*0vCmV8s*MT5tJl3_1$$wxx5aHdWPouHfaV0'}, {'domain': '.aliyun.com', 'httpOnly': False, 'name': 'login_aliyunid', 'path': '/', 'secure': False, 'value': '"%E8%BD%BB%E7%82%B9%E4%BC%81%E4%B8%9A%E5%8F%B7"'}]
    # for i in a:
    #     cookie +=i['name']+':'+i['value']+";"
    # print(cookie[:-1])
