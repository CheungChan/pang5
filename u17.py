import os
import time

from logzero import logger

from data import data
from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie, clear_and_send_keys, \
    scroll_to, click, click_by_pg

COOKIE_DOMAIN = '.u17.com'
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{data["u17_username"]}.cookie.json'
LOGIN_URL = 'http://passport.u17.com/member_v2/login.php?url=http%3A%2F%2Fcomic.user.u17.com/index.php'
AUTH_OK_URL = 'http://comic.user.u17.com/index.php'


class U17:
    def process(self):
        with open_driver(cookie_domain=COOKIE_DOMAIN,
                         cookie_file=COOKIE_FILE, browser='firefox') as driver:
            with track_alert(driver):
                self.driver = driver
                get(AUTH_OK_URL)
                if get_current_url() != AUTH_OK_URL:
                    if not self.login():
                        logger.error('登录失败')
                        return
                # store_cookie(driver, COOKIE_FILE)
                logger.info('登录成功')

                logger.info('点击新建章节')
                new_chapter_url = f'http://comic.user.u17.com/chapter/chapter_add.php?comic_id={data["u17_comic_id"]}'
                self.driver.get(new_chapter_url)
                self.publish()

    def login(self):
        login_url = get_current_url()
        js = f'''$("#login_username").val("{data['u17_username']}"); $("#login_pwd").val("{data["u17_password"]}"); $("a.login_btn:nth-child(4)").click();'''
        self.driver.execute_script(js)
        time.sleep(3)
        if get_current_url() != AUTH_OK_URL:
            input('请处理登录异常，之后按回车键')
        return get_current_url() != login_url

    def publish(self):
        logger.info('点击关闭提示')
        self.driver.find_element_by_css_selector('a.close_tip:nth-child(2)').click()

        logger.info('填写章节名称')
        clear_and_send_keys("#chapter_name", data['u17_series'])

        logger.info('上传封面图片')
        time.sleep(2)
        # self.driver.find_element_by_css_selector('div.bg_cover_box > #upload_image').click()
        # click_by_actionchains("#upload_image")
        POSOTION_GREEN_BUTTON = (1068, 885)
        click_by_pg(*POSOTION_GREEN_BUTTON)
        time.sleep(2)
        img: str = data['u17_chapter']
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
        scroll_to()
        # self.driver.find_element_by_css_selector('span.csbtn').click()
        POSOTION_GREEN_BUTTON = (784, 1108)
        click_by_pg(*POSOTION_GREEN_BUTTON)
        img: str = ' '.join(data['u17_pic'])
        cmd = f'D:/uploadImg.exe 打开 {img}'
        logger.info(cmd)
        os.system(cmd)

        logger.info('点击开始上传')
        time.sleep(2)
        self.driver.find_element_by_css_selector('#btn_start').click()
        while True:
            li_ele = self.driver.find_elements_by_css_selector('#image_list > li')
            if all([li.get_attribute('message') == '上传完毕' for li in li_ele]):
                logger.info('上传完毕')
                break
            logger.info('上传中')
            time.sleep(2)

        logger.info('提交审核')
        self.driver.find_element_by_css_selector('#main > div.borbox > div > div.tc > a').click()
        logger.info('发布成功')


def main():
    U17().process()


if __name__ == '__main__':
    main()