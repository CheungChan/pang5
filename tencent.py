import time
import os
from logzero import logger
from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie, clear_and_send_keys, \
    get_sorted_imgs, use_flash, scroll_to,click_by_actionchains,click_by_pg

pwd = os.path.abspath(os.curdir)
# 管理页面URL
MANAGE_URL = 'http://ac.qq.com/MyComic'
# 登录成功之后跳转的URL
AUTH_OK_URL = 'http://ac.qq.com/MyComic?auth=1'
USERNAME = "1042521247"
PASSWORD = "qingdian171717"
COOKIE_DOMAIN = ".ac.qq.com"
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{USERNAME}.cookie.json'
data = {
    'use-appoint': True, ""
                         'chapter-publish-time': '2018-03-24 14:00:00',
    'chapter_title': '叫什么好呢',
    'tips-chapter': os.path.join(pwd, 'images', '标题.jpg'),
    'pics': get_sorted_imgs(os.path.join(pwd, 'images', '章节'))
}
FIRST_CHAPTER = True


class Tencent:
    def __init__(self):
        pass

    def process(self):
        with open_driver(cookie_domain=COOKIE_DOMAIN,
                         cookie_file=COOKIE_FILE) as driver:
            with track_alert(driver):
                self.driver = driver

                # 处理登录
                add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
                get(MANAGE_URL)
                if get_current_url() != MANAGE_URL:
                    if not self.login():
                        logger.error('登录失败')
                        return
                store_cookie(driver, COOKIE_FILE)
                logger.info('登录成功')

                # 点击章节管理
                self.driver.find_element_by_link_text("章节管理").click()
                # self.driver.find_element_by_css_selector(".h_btn_section").click()

                # 点击新建章节
                self.driver.find_element_by_link_text("新建章节").click()

                # 让网站允许Flash
                use_flash()

                # 进入上传章节页面
                if not FIRST_CHAPTER:

                    # 有了第一章之后才会出来是否定时发布和发布日期,请提前发布好第一章
                    if data['use-appoint'] == False:
                        # 定时发布选否
                        self.driver.find_element_by_css_selector(
                            'table > tbody > tr:nth-child(2) > td.chapter-publish-time > label:nth-child(2) > input[type="radio"]').click()
                    else:
                        # 发布日期
                        self.driver.find_element_by_css_selector("#chapter_date").send_keys(
                            data['chapter-publish-time'])

                # 章节名称
                clear_and_send_keys("#chapter_title", data['chapter_title'])
                # 确定修改
                self.driver.find_element_by_css_selector("#chapterTitleSubmit").click()

                # 章节封面
                tips_chapter = data["tips-chapter"]
                logger.info(tips_chapter)
                self.driver.find_element_by_css_selector("#Filedata").send_keys(tips_chapter)

                # 点击上传封面
                time.sleep(3)
                self.driver.find_element_by_css_selector('#btn_upload').click()
                time.sleep(3)
                # 上传章节内容
                scroll_to()
                self.driver.execute_script('document.querySelectorAll("#button_main")[0].style.display="block";')
                click_by_pg(1599,749)
                #1599 749
                # toDO 上传图片选择图片并点击打开

    def login(self):
        login_url = get_current_url()
        self.driver.switch_to.frame('login_ifr')
        self.driver.find_element_by_css_selector("#switcher_plogin").click()
        clear_and_send_keys("#u", USERNAME)
        clear_and_send_keys("#p", PASSWORD)
        time.sleep(2)
        self.driver.find_element_by_css_selector("#login_button").click()
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            input('请处理登录异常，之后按回车键')
        return get_current_url() != login_url


if __name__ == '__main__':
    Tencent().process()
