import os
import time

import logzero
from logzero import logger

from config import BROWSER_FIREFOX, LOGFILE_NAME, DATA_WORKS_IMAGE, DATA_CHAPTER_IMAGE, DATA_CHAPTER_NAME, \
    DATA_PASSWORD, DATA_USERNAME, DATA_THIRD_ID, DATA_IS_CLOCK, \
    DATA_CLOCK_PUBLISH_DATETIME, DATA_PLATFORM, PLATFORM_STATUS_AUTH_FAIL, PLATFORM_STATUS_AUTH_OK
from data import data
from utils import open_driver, track_alert, get, get_current_url, clear_and_send_keys, \
    scroll_to, click_by_pyautogui, g_mysqlid, Pang5Exception, update_login_status

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
# 管理页面URL
MANAGE_URL = 'http://ac.qq.com/MyComic'
# 登录成功之后跳转的URL
AUTH_OK_URL = 'http://ac.qq.com/MyComic?auth=1'

FIRST_CHAPTER = True
REAL_PUBLISH = True
browser = BROWSER_FIREFOX

DELETE_OK_PNG = 'tencent_delete_ok.png'
CHAPTER_PNG = 'tencent.png'


class Qq:
    def __init__(self):
        logger.info(data)

    def process(self, mysql_id):
        g_mysqlid["mysql_id"] = mysql_id
        with open_driver(browser=browser) as driver:
            with track_alert(driver):
                self.driver = driver

                # 处理登录
                # add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
                # driver.get('http://www.baidu.com')
                time.sleep(5)
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if not self.login():
                        status = PLATFORM_STATUS_AUTH_FAIL
                        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                            platform_password=data[DATA_PASSWORD], platform_status=status)
                        raise Pang5Exception('登录失败')
                # store_cookie(driver, COOKIE_FILE)
                self.driver.switch_to.default_content()
                logger.info('登录成功')

                # 点击章节管理
                url = f'http://ac.qq.com/MyComic/chapterList/id/{data[DATA_THIRD_ID]}'
                logger.info(url)
                driver.get(url)
                # self.driver.find_element_by_css_selector(".h_btn_section").click()

                # 点击新建章节
                time.sleep(2)
                self.driver.find_element_by_link_text("新建章节").click()

                self.publish()

                # self.delete_all_chaptor()
                # time.sleep(1000000)

    def login(self) -> bool:
        login_url = get_current_url()
        self.driver.switch_to.frame('login_ifr')
        self.driver.find_element_by_css_selector("#switcher_plogin").click()
        clear_and_send_keys("#u", data[DATA_USERNAME])
        time.sleep(1)
        clear_and_send_keys("#p", data[DATA_PASSWORD])
        time.sleep(2)
        self.driver.find_element_by_css_selector("#login_button").click()
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            logger.info(get_current_url())
            status = PLATFORM_STATUS_AUTH_FAIL
            update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                                platform_password=data[DATA_PASSWORD], platform_status=status)
            raise Pang5Exception("登录异常")
        ok = get_current_url() != login_url
        status = PLATFORM_STATUS_AUTH_OK if ok else PLATFORM_STATUS_AUTH_FAIL
        update_login_status(platform=data[DATA_PLATFORM], platform_username=data[DATA_USERNAME],
                            platform_password=data[DATA_PASSWORD], platform_status=status)
        return True

    def publish(self):
        # 让网站允许Flash
        # use_flash()

        # 进入上传章节页面
        if not FIRST_CHAPTER:

            # 有了第一章之后才会出来是否定时发布和发布日期,请提前发布好第一章
            if data[DATA_IS_CLOCK] == False:
                # 定时发布选否
                self.driver.find_element_by_css_selector(
                    'table > tbody > tr:nth-child(2) > td.chapter-publish-time > label:nth-child(2) > input[type="radio"]').click()
            else:
                # 发布日期
                self.driver.find_element_by_css_selector("#chapter_date").send_keys(
                    data[DATA_CLOCK_PUBLISH_DATETIME])

        # 章节名称
        clear_and_send_keys("#chapter_title", data[DATA_CHAPTER_NAME])
        # 确定修改
        self.driver.find_element_by_css_selector("#chapterTitleSubmit").click()

        # 章节封面
        tips_chapter = data[DATA_WORKS_IMAGE]
        logger.info(tips_chapter)
        self.driver.find_element_by_css_selector("#Filedata").send_keys(tips_chapter)

        # 点击上传封面
        time.sleep(3)
        self.driver.find_element_by_css_selector('#btn_upload').click()
        time.sleep(3)
        # 上传章节内容
        scroll_to()
        # self.driver.execute_script('document.querySelectorAll("#button_mid")[0].style.display="block";')
        # time.sleep(1)
        # 点击上传按钮
        # d = self.driver.find_element_by_css_selector("#create_chapter_tip").location_once_scrolled_into_view
        # printt(d['x'],d['y'])
        click_by_pyautogui(CHAPTER_PNG)
        # click_by_pg(*POSOTION_GREEN_BUTTON)
        img: str = ' '.join(data[DATA_CHAPTER_IMAGE])
        cmd = f'D:/uploadImg.exe 打开 {img}'
        logger.info(cmd)
        os.system(cmd)
        js = 'return $("#uploadProgressBox").text();'
        while True:
            percent = self.driver.execute_script(js)
            time.sleep(4)
            logger.info(percent)
            if percent == '100%':
                break
        if REAL_PUBLISH:
            create_url = get_current_url()
            self.driver.find_element_by_css_selector('#submit_data').click()
            time.sleep(2)
            if create_url == get_current_url():
                logger.error(f'发布失败')
                err_msg_eles = self.driver.find_elements_by_css_selector("#cover_msg > div")
                if len(err_msg_eles) > 0:
                    err_msg = err_msg_eles[0].text
                    logger.error(err_msg)
                raise Pang5Exception('发布失败，稍后会重试')
            logger.info('发布成功')

    def delete_all_chaptor(self):
        get('http://ac.qq.com/MyComic/chapterList/id/632099')
        delete_eles = self.driver.find_elements_by_css_selector("a[do=delete]")
        while len(delete_eles) > 0:
            delete_eles[0].click()
            time.sleep(2)
            click_by_pyautogui(DELETE_OK_PNG)
            logger.info('删除章节')
            time.sleep(2)
            delete_eles = self.driver.find_elements_by_css_selector("a[do=delete]")


def main(mysql_id):
    Qq().process(mysql_id)


if __name__ == '__main__':
    main(10000)
