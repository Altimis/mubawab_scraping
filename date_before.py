import pandas as pd

import utils
from selenium.common.exceptions import NoSuchElementException
import re
from time import sleep
import random


def get_arrondissements(driver=None):
    """

    :param driver:
    :return:
    """
    if not driver:
        driver = utils.init_driver(headless=False)
    link = utils.log_search_page(driver)
    elements = driver.find_element_by_class_name('item-list'). \
        find_elements_by_xpath(".//ul/li")
    arrondissements = []
    for element in elements:
        arrondissement = element.find_element_by_xpath(".//a").text
        arrondissements.append(arrondissement)

        # print(district)
    return arrondissements


def get_offer_links(driver=None, arrondissements=None):
    """

    :param arrondissements:
    :return:
    """
    if not driver:
        driver = utils.init_driver(headless=True)
    if not arrondissements:
        with open('arrondissements_casablanca.txt') as f:
            arrondissements = f.read().splitlines()
        for arrondissement in arrondissements:
            arrondissement
    print("arrondissements :::: ", arrondissements)

    offer_links = []
    dates = []
    i = 0
    date_is_not_set = False
    for arrondissement in arrondissements:
        print(arrondissement)
        # log search page for each arrondissement
        link = "https://www.mubawab.ma/fr/crptd/casablanca-settat/" \
               "pr%C3%A9fecture-de-casablanca/casablanca/" \
               + arrondissement.lower() + "/immobilier-a-vendre"
        link = utils.log_search_page(driver, link)
        print("scraping ::: ", link)
        sleep(random.uniform(0.5, 1.5))

        # get the number of pages
        nb_element_text = driver.find_element_by_id("mainListing").find_elements_by_xpath(".//p")
        text = []
        for nb_element in nb_element_text:
            text.append(nb_element.text)
        nb_element = ' '.join([str(t) for t in text])
        # print(nb_element)
        regex = f"(\d+)-(\d+)(pages)"
        pages_nb = re.findall(regex, nb_element.strip().replace(" ", ""))[0][1]
        print("pages_nb ::: ", pages_nb)

        # loop for each page and get link of each offer
        for page in range(int(pages_nb)):
            link_page = link + ":p:" + str(int(page) + 1)
            utils.log_search_page(driver, link_page)
            offer_elements = driver.find_element_by_class_name('col-9'). \
                find_elements_by_xpath(".//ul/li")
            sleep(random.uniform(0.5, 1.5))
            for offer_element in offer_elements:
                # get link
                offer_link = offer_element.get_attribute('linkref')
                if offer_link and "https" in offer_link:
                    offer_links.append(offer_link)
                # get date
                try:
                    date = offer_element.find_element_by_xpath(".//div[2]/div[2]/span").text
                    date_before = date
                except NoSuchElementException:
                    date_is_not_set = True
                    date = str(date_before) + "<<"
                    date_before =
                print("date : ", date)
                i += 1
            sleep(random.uniform(0.5, 1.5))
            print(f"{len(offer_links)} offers retrieved until the page {page} for {arrondissement}")

    textfile = open("offer_links_casablanca.txt", "w")
    for offer_link in offer_links:
        textfile.write(offer_link + "\n")
    textfile.close()
    return offer_links


def get_data(driver=None, links=None):
    """

    :param driver:
    :param links:
    :return:
    """
    if not driver:
        driver = utils.init_driver(headless=True)
    if not links:
        with open('offer_links_casablanca.txt') as f:
            offer_links = f.read().splitlines()
    data = {'offer link': [], 'title': [], 'price': [], 'localization': [], 'description': [], 'more': [],
            'caracteristiques': []}
    not_scrapped = 0
    for i, offer_link in enumerate(offer_links):
        # exclude "immo neuf" from links
        if "/p/" in str(offer_link):
            continue
        utils.log_search_page(driver, offer_link)
        # title
        try:
            title = driver.find_element_by_class_name('searchTitle').text
        except NoSuchElementException:
            title = ""
        # price
        try:
            price = driver.find_element_by_class_name('col-7').text
        except NoSuchElementException:
            price = ""
        sleep(random.uniform(0.5, 1))
        # localization
        localization = {}
        try:
            map_element = driver.find_element_by_xpath("//a[@onclick='openHereMapClick()']")
            driver.execute_script("arguments[0].click();", map_element)
            localization['x'] = str(driver.find_element_by_id('mapOpen').get_attribute('lat'))
            localization['y'] = str(driver.find_element_by_id('mapOpen').get_attribute('lon'))
        except NoSuchElementException:
            localization['x'] = ""
            localization['y'] = ""
        sleep(random.uniform(0.5, 1))
        # descripion
        try:
            description = driver.find_element_by_class_name('blockProp').find_element_by_xpath(".//p").text
        except NoSuchElementException:
            description = ""
        # more infos
        more = []
        try:
            phys = driver.find_element_by_class_name('catNav').find_elements_by_xpath('.//span')
            for phy in phys:
                more.append(phy.text)
        except NoSuchElementException:
            more = [""]
        # caracs supp
        caracs = []
        try:
            caracs_element = driver.find_element_by_xpath('//div[@class="blockProp caractBlockProp"]/ul').\
                find_elements_by_xpath('.//li')
            for carac_element in caracs_element:
                caracs.append(carac_element.text)
        except NoSuchElementException:
            caracs = [""]
        data['offer link'].append(offer_link)
        data['title'].append(title)
        data['price'].append(price)
        data['localization'].append(localization)
        data['description'].append(description)
        data['more'].append(more)
        data['caracteristiques'].append(caracs)
        print(f"{len(data['price'])} offer(s) scrapped. The price of the last one is : {price}. Link : {offer_link}\n "
              f"and caracs : {caracs}")
        if not len(data['more']) == len(data['description']) == len(data['localization']) == len(data['price']) == len(
                data['title']) == len(data['offer link']):
            # print(f"more : {len(data['more'])}  |  description : {len(data['description'])}  |  localization : {len(data['localization'])} | "
            #       f"price : {len(data['price'])}  |  title : {len(data['title'])}  |  offer link : {len(data['offer link'])}")
            print(f"Something wrong")
            break

        # if i == 10:
        #     break
    print(f"{not_scrapped} offers not scrapped.")
    df = pd.DataFrame(data)
    df.to_csv("Mubawab_data_casablanca.csv")

    return data

def is_price(price):
    """
    match price with regex
    :param price:
    :return:
    """
    return True


# arrondissements = get_arrondissements()
# textfile = open("arrondissements_casablanca.txt", "w")
# for arrondissement in arrondissements:
#     print(arrondissement)
#     arrondissement = arrondissement.replace(" ", '-')
#     print(arrondissement)
#     textfile.write(arrondissement + "\n")
# textfile.close()

get_offer_links()
# get_data()
