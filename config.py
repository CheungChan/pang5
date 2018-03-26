import platform

USE_FACE = True
CHROME_DRIVER_PATH = 'D:/chromedriver.exe' if platform.system() == 'Windows' else '/usr/bin/chromedriver'
PHANTOMJS_PATH = ''
SCREENSHOT_PATH = 'screenshot'
# 等待类型
WAIT_PRESENCE = 'presence'
WAIT_VISIABLITY = "visiablity"
WAIT_CLICKABLE = 'clickable'
CHROME_ARG = [
    '--disable-component-update',
    '--allow-outdated-plugins',
    r'ppapi-flash-path=C:\Users\CheungChan\AppData\Local\Google\Chrome\User Data\PepperFlash\29.0.0.113\pepflashplayer.dll',
    'lang=zh_CN.UTF-8',
    '--start-maximized',
]

