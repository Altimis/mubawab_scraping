from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

import random
import time
from time import sleep



def init_driver(headless=True, proxy=None, show_images=False, option=None):
    """ initiate a chromedriver instance
        --option : other option to add (str)
    """

    # create instance of web driver
    chromedriver_path = chromedriver_autoinstaller.install()
    # options
    options = Options()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument('--disable-gpu')
        options.headless = True
    else:
        options.headless = False
    options.add_argument('log-level=3')
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)
        print("using proxy : ", proxy)
    if show_images == False:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    if option is not None:
        options.add_argument(option)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2})
    driver = webdriver.Chrome(options=options, executable_path=chromedriver_path)
    driver.set_page_load_timeout(100)
    return driver


def log_search_page(driver, link=None):
    if not link:
        link = 'https://www.mubawab.ma/fr/mprpt/casablanca-settat/pr%C3%A9fecture-de-casablanca/casablanca/immobilier' \
               '-a-vendre'
    time.sleep(1.5)
    driver.get(link)
    time.sleep(1.5)
    return link
