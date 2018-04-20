import os
import time

from logzero import logger

from config import BROWSER_CHROME,BROWSER_FIREFOX
from data import data
from utils import open_driver, track_alert, get, get_current_url, clear_and_send_keys, \
    scroll_to, click_by_pg, click_by_sikulix

# 管理页面URL
MANAGE_URL = 'http://ac.qq.com/MyComic'
# 登录成功之后跳转的URL
AUTH_OK_URL = 'http://ac.qq.com/MyComic?auth=1'

COOKIE_DOMAIN = ".ac.qq.com"
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{data["qq_username"]}.cookie.json'

FIRST_CHAPTER = True
REAL_PUBLISH = True
browser = BROWSER_FIREFOX

# POSOTION_GREEN_BUTTON = (1599, 749)
POSOTION_GREEN_BUTTON = (678, 219)


class Tencent:
    def __init__(self):
        pass

    def process(self):
        with open_driver(cookie_domain=COOKIE_DOMAIN,
                         cookie_file=COOKIE_FILE, browser=browser) as driver:
            with track_alert(driver):
                self.driver = driver

                # 处理登录
                # add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
                # driver.get('http://www.baidu.com')
                time.sleep(5)
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if not self.login():
                        logger.error('登录失败')
                        return
                # store_cookie(driver, COOKIE_FILE)
                self.driver.switch_to.default_content()
                logger.info('登录成功')

                # 点击章节管理
                url = f'http://ac.qq.com/MyComic/chapterList/id/{data["qq_comic_id"]}'
                logger.info(url)
                driver.get(url)
                # self.driver.find_element_by_css_selector(".h_btn_section").click()

                # 点击新建章节
                time.sleep(2)
                self.driver.find_element_by_link_text("新建章节").click()

                self.publish()

                # self.delete_all_chaptor()
                # time.sleep(1000000)

    def login(self):
        login_url = get_current_url()
        self.driver.switch_to.frame('login_ifr')
        self.driver.find_element_by_css_selector("#switcher_plogin").click()
        clear_and_send_keys("#u", data["qq_username"])
        clear_and_send_keys("#p", data["qq_password"])
        time.sleep(2)
        self.driver.find_element_by_css_selector("#login_button").click()
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            logger.info(get_current_url())
            input('请处理登录异常，之后按回车键')
        return get_current_url() != login_url

    def publish(self):
        # 让网站允许Flash
        # use_flash()

        # 进入上传章节页面
        if not FIRST_CHAPTER:

            # 有了第一章之后才会出来是否定时发布和发布日期,请提前发布好第一章
            if data['qq_use-appoint'] == False:
                # 定时发布选否
                self.driver.find_element_by_css_selector(
                    'table > tbody > tr:nth-child(2) > td.chapter-publish-time > label:nth-child(2) > input[type="radio"]').click()
            else:
                # 发布日期
                self.driver.find_element_by_css_selector("#chapter_date").send_keys(
                    data['qq_chapter-publish-time'])

        # 章节名称
        clear_and_send_keys("#chapter_title", data['qq_chapter_title'])
        # 确定修改
        self.driver.find_element_by_css_selector("#chapterTitleSubmit").click()

        # 章节封面
        tips_chapter = data["qq_tips-chapter"]
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
        click_by_sikulix('tencent.png')
        # click_by_pg(*POSOTION_GREEN_BUTTON)
        img: str = ' '.join(data['qq_pics'])
        cmd = f'D:/uploadImg.exe 打开 {img}'
        logger.info(cmd)
        os.system(cmd)
        js = 'return $("#uploadProgressBox").text();'
        while True:
            percent = self.driver.execute_script(js)
            time.sleep(1)
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
                input('发布失败，请查看')
            logger.info('发布成功')

    def delete_all_chaptor(self):
        import pyautogui as pg
        get('http://ac.qq.com/MyComic/chapterList/id/632099')
        delete_eles = self.driver.find_elements_by_css_selector("a[do=delete]")
        while len(delete_eles) > 0:
            delete_eles[0].click()
            time.sleep(2)
            pg.press('enter')
            logger.info('删除章节')
            time.sleep(2)
            delete_eles = self.driver.find_elements_by_css_selector("a[do=delete]")


def main():
    Tencent().process()


if __name__ == '__main__':
    main()
