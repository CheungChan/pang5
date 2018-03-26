import platform

USE_FACE = True
CHROME_DRIVER_PATH = 'D:/chromedriver.exe' if platform.system() == 'Windows' else '/usr/bin/chromedriver'
PHANTOMJS_PATH = ''
SCREENSHOT_PATH = 'screenshot'
# 等待类型
WAIT_PRESENCE = 'presence'
WAIT_VISIABLITY = "visiablity"
WAIT_CLICKABLE = 'clickable'
