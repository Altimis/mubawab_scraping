import config
import random
import time
from time import sleep

import gridfs
import requests
from pymongo import MongoClient

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller


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
    if not show_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    if option is not None:
        options.add_argument(option)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2})
    driver = webdriver.Chrome(options=options, executable_path=chromedriver_path)
    driver.set_page_load_timeout(100)
    return driver


def log_in(driver, timeout=10):
    """
	Log in to facebook
	"""
    print("-------- Authentification ---------")
    driver.get('https://www.facebook.com/')
    username_xpath = './/input[@id="email"]'
    password_xpath = './/input[@id="pass"]'
    try:
        username_el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, username_xpath)))
        password_el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, password_xpath)))
        username_el.send_keys(config.username)
        password_el.send_keys(config.password)
        password_el.send_keys(Keys.RETURN)

        print("Authentification is done.")
    except:
        print("Authentification failed.")


def log_search_page(driver):
    search = "%20".join(config.search_req.split(" "))
    path = 'https://www.facebook.com/search/posts/?q=' + search
    time.sleep(1.4)
    driver.get(path)
    time.sleep(1.5)
    return path


def keep_scroling(driver, scrolling, posts_parsed, limit, scroll, last_position, words=None):
    """ scrolling function for pubs crawling"""

    global pub_link
    print("starts scrolling")
    while scrolling and posts_parsed < limit:
        sleep(random.uniform(0.5, 1.5))
        scroll_attempt = 0
        while True:
            # check scroll position
            scroll += 1
            print("scroll ", scroll)
            sleep(random.uniform(0.5, 1.5))
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                # end of scroll region
                if scroll_attempt >= 3:
                    scrolling = False
                    break
                else:
                    sleep(random.uniform(0.5, 1.5))  # attempt another scroll
            else:
                last_position = curr_position
                break

    print("End of scrolling")
    page_cards = driver.find_elements_by_xpath('//div[@role="article"]')
    print("Number of posts: ", len(list(page_cards)))
    links = []
    for i, card in enumerate(page_cards):
        try:
            pub_link = card.find_element_by_css_selector(
                "[class = 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 a8c37x1j p7hjln8o "
                "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of "
                "lzcic4wl gmql0nx0 p8dawk7l'").get_attribute(
                'href')
        except Exception as e:
            print("01 : ", e)
        sleep(random.uniform(0.5, 1.5))
        if pub_link is None:
            return
        pub_link = pub_link.replace("/web.", "/www.")
        links.append(str(pub_link))
    print(f"{len(links)} posts to be fetched.")
    return links


def get_data(driver, links):
    """Extract caption, comments and images links given the posts links"""
    image_links = {}
    captions = {}
    comments = {}

    for i, link in enumerate(links):
        print("Extracting data from the post with the link : ", link)
        sleep(2)
        # load post page
        driver.get(link)

        ################ caption data
        sleep(2)
        if "/photos/" in link:
            # TODO: get caption for this case
            #             print("photos")
            # continue in this case
            continue
        else:
            # get the
            text_elements = driver.find_elements_by_css_selector(
                "[class = 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d3f4x2em "
                "fe6kdd0r mau55g9w c8b282yb iv3no6db jq4qci2q a3bd9o3v b1v8xokw oo9gr5id hzawbc8m'")
            print("Extracting the caption")
            sleep(1)
            if len(text_elements) == 0:
                # continue if there is no caption
                continue
            for text_element in text_elements:
                # select the text caption among all these elements (which is the first element in the list)
                text = str(text_element.text)
                if len(text) != 0:
                    captions[i] = text
                    print("Done.\n", text)
                    break

        #################### commets
        try:
            # get the elements that contain comments (<li> in this case)
            comments_element = driver.find_elements_by_xpath('//li')
            comments_text = []
            # iterate for each element
            for comment_element in comments_element:
                try:
                    # get text comment from the element
                    text_comment = comment_element.find_element_by_css_selector(
                        "[class = 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j keod5gw0 nxhoafnm aigsh9s9 "
                        "d3f4x2em fe6kdd0r mau55g9w c8b282yb iv3no6db jq4qci2q a3bd9o3v b1v8xokw oo9gr5id'")
                    comment = str(text_comment.text)
                    comments_text.append(comment)
                except:
                    # continue if the comment is not readable
                    continue
            comments[i] = comments_text
        except:
            # save empty list if there is no comments
            comments[i] = []

        ################# images
        try:
            # try to get the element that contains the image
            image_element = driver.find_element_by_css_selector(
                "[class = 'oajrlxb2 gs1a9yip g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 goun2846 ccm00jje s44p3ltw "
                "mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv nhd2j8a9 a8c37x1j mg4g778l btwxx1t3 pfnyh3mw "
                "p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x tgvbjcpo hpfvmrgz jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso "
                "l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of du4w35lb lzcic4wl n00je7tq arfg74bv qs9ysxi8 k77z8yql abiwlrkh "
                "p8dawk7l tm8avpzi'")
            image_link = image_element.find_element_by_xpath('.//img').get_attribute('src')
            image_links[i] = image_link
            print(image_link)
        except:
            image_links[i] = ""
            print("No image to capture.")

    data = {"Caption": captions, "Comments": comments, "Images links": image_links}
    return data


def save_images(db, urls):
    """download images and store them in mongodb"""
    fs = gridfs.GridFS(db)
    for i, url in enumerate(urls):
        img_data = requests.get(url).content
        fs.put(img_data, filename="file")


def store_to_mongo(data, db_name):
    """store data to mongodb"""
    client = MongoClient(host="localhost", port=27017)
    mydb = client[db_name]
    posts = mydb.posts
    for post in data:
        # print(post)
        posts.insert_one(post)
    # save images to db
    urls = []
    for d in data:
        urls.append(d["Images links"])
    save_images(mydb, urls)
