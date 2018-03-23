from utils import open_driver, track_alert,get,click,store_cookie,add_cookie,get_current_url
import time
from logzero import logger
MANAGE_URL='https://zz.manhua.163.com/'
COOKIE_DOMAIN = ".manhua.163.com"
USERNAME='18101038354'
COOKIE_FILE = f'cookies/{COOKIE_DOMAIN[1:]}_{USERNAME}.cookie.json'
from selenium.webdriver.support.ui import WebDriverWait
def main():
    with open_driver(cookie_domain=".manhua.163.com",
                         cookie_file=COOKIE_FILE) as driver:
        with track_alert(driver):

            # 处理登录
            add_cookie(COOKIE_DOMAIN, driver, COOKIE_FILE)
            get(MANAGE_URL)
            if get_current_url() != MANAGE_URL:
                login(driver)
                store_cookie(driver, COOKIE_FILE)
                logger.info('登录成功')
            #登录
            #继续中间页面
                get('http://zz.manhua.163.com/')
            click('.add')
            time.sleep(3)

            js = "$('input').attr('readonly','')"
            driver.execute_script(js)
            time.sleep(3)
            title = driver.find_element_by_id('title')
            title.send_keys('胖5号')
            time.sleep(3)
            file=driver.find_element_by_css_selector('.webuploader-element-invisible')
            file.send_keys('/home/hgzyc/wechat.png')
            driver.find_element_by_id('timing_flag').click()


            autoPublishDate=driver.find_element_by_css_selector('#timing > div > div.small-4.columns > input[type="text"]')
            autoPublishDate.send_keys('2019-01-01')
            time.sleep(10)
            # driver.find_element_by_css_selector('body > section:nth-child(2) > div > div.large-9.medium-8.columns > div > form > div:nth-child(9) > div.small-10.columns > button.small.btn-normal.right').click()
            time.sleep(1000)
def login(driver):

        get('https://manhua.163.com/')
        # click('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required')
        driver.find_element_by_css_selector('.topbar-meta-user >ul >li:nth-child(1)>.js-login-required').click()

        # driver.find_element_by_css_selector('.sns-mobile').click()
        click('.sns-mobile')
        time.sleep(1)
        username = driver.find_element_by_id('username')

        username.send_keys('18101038354')
        password = driver.find_element_by_id('password')
        password.send_keys('qingdian')
        driver.find_element_by_css_selector('form.login-classic > div:nth-child(8) > button').click()

        return driver

if __name__ == '__main__':
    main()
