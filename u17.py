import os
import time
from datetime import datetime, timedelta
import logzero
from logzero import logger
from selenium.common.exceptions import JavascriptException

from config import LOGFILE_NAME, DATA_CHAPTER_IMAGE, DATA_CHAPTER_NAME, DATA_PASSWORD, DATA_USERNAME, DATA_THIRD_ID, \
    DATA_WORKS_IMAGE, PLATFORM_STATUS_AUTH_OK, PLATFORM_STATUS_AUTH_FAIL, DATA_PLATFORM, DATA_LOGIN_TYPE, DATA_IS_CLOCK, \
    DATA_CLOCK_PUBLISH_DATETIME, DATA_NEXT_TIME
from data import data
from utils import open_driver, track_alert, get, get_current_url, clear_and_send_keys, \
    scroll_to, click_by_pyautogui, Pang5Exception, update_status2OK, g_mysqlid, scroll_to_id, update_login_status

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
LOGIN_URL = 'http://passport.u17.com/member_v2/login.php?url=http%3A%2F%2Fcomic.user.u17.com/index.php'
LOGIN_MOBILE_URL = 'http://m.u17.com/Wap/login/login?type=personal'
AUTH_OK_URL = 'http://comic.user.u17.com/index.php'
AUTH_MOBILE_OK_URL = 'http://m.u17.com/wap/Personal/index'
TITLE_PNG = 'u17_title.png'
CHAPTER_PNG = 'u17_chapter.png'
START_UPLOAD_PNG = 'u17_start_upload.png'


class U17:
    def __init__(self):
        logger.info(data)

    def process(self, mysql_id):
        g_mysqlid["mysql_id"] = mysql_id
        with open_driver(browser='firefox') as driver:
            with track_alert(driver):
                self.driver = driver
                get(AUTH_OK_URL)
                if get_current_url() != AUTH_OK_URL:

                    # 登录方式
                    login_type = data[DATA_LOGIN_TYPE]
                    if login_type in ('', 'mobile', 'email', 'mail', 'username'):
                        login = self.login_mobile
                    elif login_type == 'qq':
                        login = self.login_mobile_qq
                    elif login_type == 'weibo':
                        login = self.login_mobile_weibo
                    else:
                        raise Pang5Exception(f'登录方式不支持{login_type}')

                    if not login():
                        status = PLATFORM_STATUS_AUTH_FAIL
                        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                            platform_password=data[DATA_PASSWORD], platform_status=status)
                        raise Pang5Exception("登录失败")
                logger.info('登录成功')

                logger.info('点击新建章节')
                new_chapter_url = f'http://comic.user.u17.com/chapter/chapter_add.php?comic_id={data[DATA_THIRD_ID]}'
                self.driver.get(new_chapter_url)
                time.sleep(3)
                if get_current_url() != new_chapter_url:
                    raise Pang5Exception('有妖气作品id有误')
                self.publish()

    def login(self) -> bool:
        login_url = get_current_url()
        js = f'''$("#login_username").val("{data[DATA_USERNAME]}"); $("#login_pwd").val("{data[DATA_PASSWORD]}"); $("a.login_btn:nth-child(4)").click();'''
        self.driver.execute_script(js)
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            status = PLATFORM_STATUS_AUTH_FAIL
            update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                platform_password=data[DATA_PASSWORD], platform_status=status)
            raise Pang5Exception("登录失败")
        status = PLATFORM_STATUS_AUTH_OK
        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                            platform_password=data[DATA_PASSWORD], platform_status=status)
        return True

    def login_mobile(self) -> bool:
        self.driver.get(LOGIN_MOBILE_URL)
        self.driver.find_element_by_css_selector('#wrapper > div > div:nth-child(2) > input').send_keys(
            data[DATA_USERNAME])
        self.driver.find_element_by_css_selector('#wrapper > div > div:nth-child(3) > input:nth-child(1)').send_keys(
            data[DATA_PASSWORD])
        time.sleep(1)
        self.driver.find_element_by_css_selector('#wrapper > div > a.green-btn.login-btn').click()
        time.sleep(2)
        ok = get_current_url() == AUTH_MOBILE_OK_URL
        status = PLATFORM_STATUS_AUTH_OK if ok else PLATFORM_STATUS_AUTH_FAIL
        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                            platform_password=data[DATA_PASSWORD], platform_status=status)
        return ok

    def login_mobile_qq(self):
        self.driver.get(LOGIN_MOBILE_URL)
        # 点击qq
        self.driver.find_element_by_css_selector('#coagent > a.coagent.coagent-qq').click()
        time.sleep(1)

        self.driver.switch_to_frame(self.driver.find_element_by_id("ptlogin_iframe"))
        self.driver.find_element_by_id('switcher_plogin').click()
        time.sleep(3)
        u = self.driver.find_element_by_id('u')
        u.clear()
        u.send_keys(data[DATA_USERNAME])
        p = self.driver.find_element_by_id('p')
        p.clear()
        p.send_keys(data[DATA_PASSWORD])
        self.driver.find_element_by_id('login_button').click()
        time.sleep(3)
        ok = get_current_url() == AUTH_MOBILE_OK_URL
        status = PLATFORM_STATUS_AUTH_OK if ok else PLATFORM_STATUS_AUTH_FAIL
        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                            platform_password=data[DATA_PASSWORD], platform_status=status)
        return ok

    def login_mobile_weibo(self):
        self.driver.get(LOGIN_MOBILE_URL)
        # 点击微博
        self.driver.find_element_by_css_selector('a.coagent-weibo:nth-child(2)').click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('#userId').send_keys(data[DATA_USERNAME])
        self.driver.find_element_by_css_selector('#passwd').send_keys(data[DATA_PASSWORD])
        time.sleep(1)
        self.driver.find_element_by_css_selector('.WB_btn_login').click()
        time.sleep(3)
        ok = get_current_url() == AUTH_MOBILE_OK_URL
        status = PLATFORM_STATUS_AUTH_OK if ok else PLATFORM_STATUS_AUTH_FAIL
        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                            platform_password=data[DATA_PASSWORD], platform_status=status)
        return ok

    def publish(self):
        logger.info('点击关闭提示')
        try:
            scroll_to()
            self.driver.find_element_by_css_selector('a.close_tip:nth-child(2)').click()
        except:
            logger.info('没有关闭提示')
        logger.info('隐藏选择适合自己的字号')
        try:
            # js = '$("body > div.font_tip_dialog").hide()'
            js = 'document.querySelector("body > div.font_tip_dialog").style.display = "none";'
            self.driver.execute_script(js)
        except JavascriptException as e:
            logger.error(e)
        time.sleep(1)
        scroll_to_id('chapter_name')
        logger.info('填写章节名称')
        clear_and_send_keys("#chapter_name", data[DATA_CHAPTER_NAME])

        logger.info('上传封面图片')
        time.sleep(2)
        click_by_pyautogui(TITLE_PNG)
        time.sleep(2)
        img: str = data[DATA_WORKS_IMAGE]
        cmd = f'D:/uploadImg.exe 打开 {img}'
        logger.info(cmd)
        os.system(cmd)
        while True:
            loading_ele = self.driver.find_element_by_css_selector('.loading_tm > img:nth-child(1)')
            if not loading_ele.is_displayed():
                logger.info('封面上传完毕')
                break
            logger.info('封面正在上传中。。。')
            time.sleep(2)

        logger.info('上传章节内容')
        scroll_to_id('btn_start')
        click_by_pyautogui(CHAPTER_PNG)
        img: str = ' '.join(data[DATA_CHAPTER_IMAGE])
        cmd = f'D:/uploadImg.exe 打开 {img}'
        logger.info(cmd)
        os.system(cmd)
        time.sleep(2)
        logger.info('点击开始上传')
        scroll_to_id('btn_start')
        click_by_pyautogui(START_UPLOAD_PNG)
        start = time.time()

        while True:
            li_ele = self.driver.find_elements_by_css_selector('#image_list > li')
            els = [li.get_attribute('message') == '上传完毕' for li in li_ele]
            count_all = len(els)
            count_ok = sum(els)
            count_lack = count_all - count_ok
            if count_lack == 0:
                logger.info('上传完毕')
                break
            if time.time() - start > 60:
                logger.error('上传图片超时')
                js = 'return $(".tipsFont").text()'
                raise Pang5Exception(self.driver.execute_script(js))
            logger.info(f'上传中, 共{count_all}个， {count_ok}个上传成功， {count_lack}个正在上传中。。。')
            time.sleep(4)

        if data[DATA_IS_CLOCK]:
            # 点击设置
            # self.driver.find_element_by_css_selector('#open_release_time > span').click()
            publish_datetime = data[DATA_CLOCK_PUBLISH_DATETIME]
            if len(publish_datetime) == len('2010-10-10 04:00'):
                publish_datetime = publish_datetime + ':00'
            js = f'$("#input_release_time").val("{publish_datetime}")'
            logger.info(js)
            self.driver.execute_script(js)
            logger.info(f'设置定时时间为{publish_datetime}')

            # 暂时将下次更新时间设置为2天后.
            two_days_from_now = data[DATA_NEXT_TIME] or (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            js = f'$("#input_update_time").val("{two_days_from_now}")'
            logger.info(js)
            self.driver.execute_script(js)
            logger.info(f'设置下次更新时间为{two_days_from_now}')

        logger.info('提交审核')
        self.driver.find_element_by_css_selector('#main > div.borbox > div > div.tc > a').click()
        logger.info('发布成功')
        error_msg = self.driver.find_elements_by_css_selector('#messageBox1 > table > tbody > tr > td')
        if len(error_msg) == 1:
            raise Pang5Exception(error_msg[0].text)
        update_status2OK()


def main(mysql_id):
    U17().process(mysql_id)


if __name__ == '__main__':
    main(10000)
