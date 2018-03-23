import time

from logzero import logger

from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie

MANAGE_URL = 'http://ac.qq.com/MyComic'
USERNAME = "1042521247"
PASSWORD = "qingdian171717"
COOKIE_DOMAIN = ".qq.com"
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{USERNAME}.cookie.json'
data = {
    'use-appoint': True,
    'chapter-publish-time': '2018-03-24 14:00:00',
    'chapter_title': '叫什么好呢',
    'tips-chapter': '/Users/chenzhang/Pictures/封面.jpg',
    'pics': [
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_01.jpg',
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_02.jpg',
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_03.jpg',
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_04.jpg',
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_05.jpg',
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_06.jpg',
        '/Users/chenzhang/Pictures/文章封面/20171031174631_rXO8gMcPUc_07.jpg',
    ]
}


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

                # 进入上传章节页面


                # 有了第一章之后才会出来是否定时发布和发布日期,请提前发布好第一章
                if data['use-appoint'] == False:
                    # 定时发布选否
                    self.driver.find_element_by_css_selector(
                        'table > tbody > tr:nth-child(2) > td.chapter-publish-time > label:nth-child(2) > input[type="radio"]').click()
                else:
                    # 发布日期
                    self.driver.find_element_by_css_selector("#chapter_date").send_keys(data['chapter-publish-time'])


                # 章节名称
                self.driver.find_element_by_css_selector("#chapter_title").send_keys(data['chapter_title'])
                # 确定修改
                self.driver.find_element_by_css_selector("#chapterTitleSubmit").click()

                # 章节封面
                self.driver.find_element_by_css_selector("#Filedata").send_keys(data["tips-chapter"])

                # 点击上传封面
                self.driver.find_element_by_css_selector('#btn_upload').click()

                # TODO 上传章节内容
                pass

    def login(self):
        login_url = get_current_url()
        self.driver.switch_to.frame('login_ifr')
        self.driver.find_element_by_css_selector("#switcher_plogin").click()
        self.driver.find_element_by_css_selector("#u").send_keys(USERNAME)
        self.driver.find_element_by_css_selector("#p").send_keys(PASSWORD)
        time.sleep(2)
        self.driver.find_element_by_css_selector("#login_button").click()
        time.sleep(3)
        return get_current_url() != login_url


if __name__ == '__main__':
    Tencent().process()
