import platform
import os
from datetime import datetime

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
SCREENSHOT_PATH = 'screenshot'
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
    MYSQL_URL = 'mysql://10.10.10.43/pang5?user=qd&password=123^%$-qwe-asd&charset=utf8mb4'

    RABBITMQ_HTOS = '10.10.10.3'
    RABBITMQ_POST = 5000
    RABBITMQ_USER = 'hgz'
    RABBITMQ_PASSWORD = 'hgz123^%$'

if __name__ == '__main__':
    print(DEBUG)
