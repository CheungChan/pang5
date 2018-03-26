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
    '—disable-bundled-ppapi-flash',
    r'ppapi-flash-path=C:\Windows\SysWOW64\Macromed\Flash\pepflashplayer32_29_0_0_113.dll',
    'lang=zh_CN.UTF-8',
    '--start-maximized',
]

