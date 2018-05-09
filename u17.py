import os
import time

import logzero
from logzero import logger

from config import LOGFILE_NAME, DATA_CHAPTER_IMAGE, DATA_CHAPTER_NAME, DATA_PASSWORD, DATA_USERNAME, DATA_THIRD_ID, \
    DATA_WORKS_IMAGE
from data import data
from utils import open_driver, track_alert, get, get_current_url, clear_and_send_keys, \
    scroll_to, click_by_pyautogui, Pang5Exception, update_status2OK, g_mysqlid, scroll_to_id

logzero.logfile(LOGFILE_NAME, encoding='utf-8', maxBytes=500_0000, backupCount=3)
LOGIN_URL = 'http://passport.u17.com/member_v2/login.php?url=http%3A%2F%2Fcomic.user.u17.com/index.php'
AUTH_OK_URL = 'http://comic.user.u17.com/index.php'
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
                    if not self.login():
                        raise Pang5Exception("登录失败")
                logger.info('登录成功')

                logger.info('点击新建章节')
                new_chapter_url = f'http://comic.user.u17.com/chapter/chapter_add.php?comic_id={data[DATA_THIRD_ID]}'
                self.driver.get(new_chapter_url)
                self.publish()

    def login(self):
        login_url = get_current_url()
        js = f'''$("#login_username").val("{data[DATA_USERNAME]}"); $("#login_pwd").val("{data[DATA_PASSWORD]}"); $("a.login_btn:nth-child(4)").click();'''
        self.driver.execute_script(js)
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            raise Pang5Exception("登录失败")
        return get_current_url() != login_url

    def publish(self):
        logger.info('点击关闭提示')
        try:
            scroll_to()
            self.driver.find_element_by_css_selector('a.close_tip:nth-child(2)').click()
        except:
            logger.info('没有关闭提示')
        logger.info('隐藏选择适合自己的字号')
        js = '$("body > div.font_tip_dialog").hide()'
        self.driver.execute_script(js)
        time.sleep(1)
        logger.info('填写章节名称')
        clear_and_send_keys("#chapter_name", data[DATA_CHAPTER_NAME])

        logger.info('上传封面图片')
        time.sleep(2)
        # self.driver.find_element_by_css_selector('div.bg_cover_box > #upload_image').click()
        # click_by_actionchains("#upload_image")
        # POSOTION_GREEN_BUTTON = (1068, 885)
        # POSOTION_GREEN_BUTTON = (439, 442)
        #
        # click_by_pg(*POSOTION_GREEN_BUTTON)
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
        scroll_to(500)
        time.sleep(1)
        # self.driver.find_element_by_css_selector('span.csbtn').click()
        # POSOTION_GREEN_BUTTON = (784, 1108)
        # POSOTION_GREEN_BUTTON = (288,304 )
        #
        # click_by_pg(*POSOTION_GREEN_BUTTON)
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
            if time.time() - start > 2 * 60:
                logger.error('上传图片超时')
                js = 'return $(".tipsFont").text()'
                raise Pang5Exception(self.driver.execute_script(js))
            logger.info(f'上传中, 共{count_all}个， {count_ok}个上传成功， {count_lack}个正在上传中。。。')
            time.sleep(4)

        logger.info('提交审核')
        self.driver.find_element_by_css_selector('#main > div.borbox > div > div.tc > a').click()
        logger.info('发布成功')
        update_status2OK()


def main(mysql_id):
    U17().process(mysql_id)


if __name__ == '__main__':
    main(10000)
