import platform
import os
from datetime import datetime
from pathlib import Path

DEBUG = False
profile_file = os.path.join(os.path.expanduser('~'), 'profile')
if os.path.exists(profile_file):
    with open(profile_file, encoding='utf-8') as f:
        if f.read().strip() == 'dev':
            DEBUG = True
USE_FACE = True
CHROME_DRIVER_PATH = 'D:/chromedriver.exe' if platform.system() == 'Windows' else '/usr/bin/chromedriver'
PHANTOMJS_PATH = ''
FIREFOX_DRIVER_PATH = 'D:/geckodriver.exe' if platform.system() == 'Windows' else '/usr/bin/geckodriver'
SCREENSHOT_PATH = str(Path(__file__).parent / 'screenshot')
CAPTCHAR_PATH = str(Path(__file__).parent / 'captcha_img')
# 等待类型
WAIT_PRESENCE = 'presence'
WAIT_VISIABLITY = "visiablity"
WAIT_CLICKABLE = 'clickable'
BROWSER_CHROME = 'chrome'
BROWSER_FIREFOX = 'firefox'
RUN_SIKULIX_CMD = r'D:\sikuli\runsikulix.cmd'
LOGFILE_NAME = f'D:/logs/pang5_{datetime.now().strftime("%Y%m%d %H%M%S")}.log' if platform.system() == 'Windows' \
    else f'/tmp/pang5_{datetime.now().strftime("%Y%m%d %H%M%S")}.log'
CHROME_ARG = [
    '--disable-component-update',
    '--allow-outdated-plugins',
    '—disable-bundled-ppapi-flash',
    r'ppapi-flash-path=C:\Windows\SysWOW64\Macromed\Flash\pepflashplayer32_29_0_0_113.dll',
    'lang=zh_CN.UTF-8',
    '--start-maximized',
]

if DEBUG:
    MYSQL_URL = 'mysql://10.10.6.2/pang5?user=develop&password=123-qwe&charset=utf8mb4'
    RABBITMQ_HTOS = '10.10.6.5'
    RABBITMQ_POST = 5672
    RABBITMQ_USER = 'yanghao'
    RABBITMQ_PASSWORD = '123456'
else:
    MYSQL_URL = 'mysql://10.10.10.43:2000/pang5?user=qd&password=123^%$-qwe-asd&charset=utf8mb4'

    RABBITMQ_HTOS = '10.10.10.3'
    RABBITMQ_POST = 5000
    RABBITMQ_USER = 'hgz'
    RABBITMQ_PASSWORD = 'hgz123^%$'

# 数据常量
# 所有的数据的键都必须用这里的常量,来确保所有平台的一致性.
DATA_PLATFORM = 'platform'  # 平台名称
DATA_LOGIN_TYPE = 'login_type'  # 登录类型
DATA_USERNAME = 'username'  # 用户名
DATA_PASSWORD = 'password'  # 密码
DATA_WORKS_NAME = 'works_name'  # 作品名称
DATA_CHAPTER_NAME = 'chapter_name'  # 章节名称
DATA_THIRD_ID = 'third_id'  # 第三方平台作品id
DATA_IS_CLOCK = 'is_clock'  # 是否定时
DATA_CLOCK_PUBLISH_DATETIME = 'clock_publish_datetime'  # 定时发布时间
DATA_WORKS_IMAGE = 'works_image'  # 作品图片
DATA_CHAPTER_IMAGE = 'chapter_image'  # 章节图片
DATA_NEXT_TIME = 'next_time'  # 只有有妖气有的下次更新时间

NEED_FLASH_PLATFORM = ('qq', 'maimeng', 'u17')

# 0待校验 1 校验通过 2 校验失败
PLATFORM_STATUS_WAIT_AUTH = 0
PLATFORM_STATUS_AUTH_OK = 1
PLATFORM_STATUS_AUTH_FAIL = 2

if __name__ == '__main__':
    print(DEBUG)
