from utils import init_driver, log_in, log_search_page, keep_scroling, store_to_mongo, get_data
import config
import random
from time import sleep


def main(words=None, headless=True, limit=float("inf"), proxy=None):
    refresh = 0
    # intiate the driver
    driver = init_driver(headless, proxy)
    # login to facebook
    log_in(driver, timeout=10)
    scroll = 0
    # log the search page according to the request
    path = log_search_page(driver=driver)
    refresh += 1
    # get the last position of the page
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True
    print(" Fetching the Link : {}".format(path))
    posts_parsed = 0
    sleep(random.uniform(0.5, 1.5))
    # get links of all posts
    links = \
        keep_scroling(driver, scrolling, posts_parsed, limit, scroll, last_position, words=words)
    # navigate to each post and get the corresponding data
    data = get_data(driver, links)
    driver.close()
    # change the data to json format
    data_json = []
    for i in range(len(data["Caption"])):
        data_json.append({"Caption": data["Caption"][i],
                          "Comments": data["Comments"][i],
                          "Images links": data["Images links"][i]})
    # store data to mongo
    store_to_mongo(data_json, config.db)
    print(data_json)
    return data_json


main(headless=True)