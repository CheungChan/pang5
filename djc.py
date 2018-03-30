import time
import os
from logzero import logger
from utils import open_driver, track_alert, get, get_current_url, add_cookie, store_cookie, clear_and_send_keys, \
    use_flash, scroll_to, click_by_pg
from data import data