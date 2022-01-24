import pandas as pd

import utils
from selenium.common.exceptions import NoSuchElementException
import re
from time import sleep
import random
import datetime
import pickle


def get_arrondissements(driver=None):
    """

    :param driver:
    :return:
    """
    link = "https://www.mubawab.ma/fr/mprpt/casablanca-settat/pr%C3%A9fecture-de-casablanca/casablanca/immobilier' \
               '-a-vendre"
    if not driver:
        driver = utils.init_driver(headless=False)
    utils.log_search_page(driver, link)
    elements = driver.find_element_by_class_name('item-list'). \
        find_elements_by_xpath(".//ul/li")
    arrondissements = []
    for element in elements:
        arrondissement = element.find_element_by_xpath(".//a").text
        arrondissements.append(arrondissement)

        # print(district)
    return arrondissements


def get_offer_links(driver=None, arrondissements=None, link_gen=None):
    """

    :param link_gen:
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

    data_arrondissement = {}
    for arrondissement in arrondissements:
        data_arrondissement[arrondissement] = {}
    for arrondissement in arrondissements:
        if arrondissement not in ["Anfa", "Maârif"]:
            continue
        print(arrondissement)
        # log search page for each arrondissement
        # link = "https://www.mubawab.ma/fr/crptd/casablanca-settat/" \
        #        "pr%C3%A9fecture-de-casablanca/casablanca/" \
        #        + arrondissement.lower() + "/immobilier-a-vendre"
        link = link_gen[0] + arrondissement.lower() + link_gen[1]
        utils.log_search_page(driver, link)
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
        offer_links = []
        dates = []
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
                else:
                    continue
                # get date
                try:
                    date = offer_element.find_element_by_xpath(".//div[2]/div[2]/span").text
                except NoSuchElementException:
                    date = ""
                # print("date : ", date)
                date_extracted = detect_date(date)
                dates.append(date_extracted)
            sleep(random.uniform(0.5, 1.5))
            # print(f"{len(offer_links)} offers retrieved until the page {page} for {arrondissement}")

        data_arrondissement[arrondissement]["links"] = offer_links
        data_arrondissement[arrondissement]["dates"] = dates
        print(
            f"{len(offer_links)} links and {len(dates)} dates retrieved from {arrondissement} "
            f"including the date : {dates[-1]}")

    a_file = open("data_arrondissement_louer_anfa_maarif.pkl", "wb")
    pickle.dump(data_arrondissement, a_file)
    a_file.close()
    return data_arrondissement


def get_data(driver=None, links=None):
    """

    :param driver:
    :param links:
    :return:
    """
    if not driver:
        driver = utils.init_driver(headless=True)
    if not links:
        a_file = open("data_arrondissement_louer_anfa_maarif.pkl", "rb")
        data = pickle.load(a_file)
    data_arrondissement = {'date': [], 'arrondissement': [], 'offer link': [], 'title': [], 'price': [],
                           'localization': [], 'description': [], 'more': [], 'caracteristiques': []}
    not_scrapped = 0
    for arr, d in data.items():
        # if arr == 'Roches-Noires':
        if arr not in ["Anfa", "Maârif"]:
            continue
        for offer_link, date in zip(d['links'], d['dates']):
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
                caracs_element = driver.find_element_by_xpath('//div[@class="blockProp caractBlockProp"]/ul'). \
                    find_elements_by_xpath('.//li')
                for carac_element in caracs_element:
                    caracs.append(carac_element.text)
            except NoSuchElementException:
                caracs = [""]
            data_arrondissement['arrondissement'].append(arr)
            data_arrondissement['date'].append(date)
            data_arrondissement['offer link'].append(offer_link)
            data_arrondissement['title'].append(title)
            data_arrondissement['price'].append(price)
            data_arrondissement['localization'].append(localization)
            data_arrondissement['description'].append(description)
            data_arrondissement['more'].append(more)
            data_arrondissement['caracteristiques'].append(caracs)
            print(f"Arrondissement : {arr} , date : {date} , {len(data_arrondissement['price'])} "
                  f"offer(s) scrapped. The price of the last one is : {price}. Link : {offer_link}\n "
                  f"and caracs : {caracs}")
            if not len(data_arrondissement['more']) == len(data_arrondissement['description']) == \
                   len(data_arrondissement['localization']) == len(data_arrondissement['price']) == \
                   len(data_arrondissement['title']) == len(data_arrondissement['offer link']) == \
                   len(data_arrondissement['date']) == len(data_arrondissement['arrondissement']):
                # print(f"more : {len(data['more'])}  |  description : {len(data['description'])}  |  localization : {len(data['localization'])} | "
                #       f"price : {len(data['price'])}  |  title : {len(data['title'])}  |  offer link : {len(data['offer link'])}")
                print(f"Something wrong")
                break
        # break
        # if i == 10:
        #     break
        print(f"{not_scrapped} offers not scrapped.")
        df = pd.DataFrame(data_arrondissement)
        df.to_csv("Mubawab_data_casablanca.csv")

    # print(f"{not_scrapped} offers not scrapped.")
    # df = pd.DataFrame(data_arrondissement)
    # df.to_csv("Mubawab_data_casablanca.csv")

    return data_arrondissement


def detect_date(date):
    """

    :return:
    """
    date = str(date)
    today = datetime.date.today().strftime("%d/%m/%Y")
    if "aujourdhui" in date or "ajourd'hui" in date:
        date_extracted = today
        return date_extracted
    if "jours" in date or "jour" in date:
        regex = f"(\d)(jour|jours)"
        days = re.findall(regex, date.strip().replace(" ", ""))[0][0]
        date_extracted = datetime.datetime.strptime(today, "%d/%m/%Y") - datetime.timedelta(days=int(days))
        return date_extracted
    if "mois" in date:
        regex = f"(\d)(mois)"
        months = re.findall(regex, date.strip().replace(" ", ""))[0][0]
        date_extracted = datetime.datetime.strptime(today, "%d/%m/%Y") - datetime.timedelta(days=int(months) * 30)
        return date_extracted
    if "semaine" in date or "semaines" in date:
        regex = f"(\d)(semaine|semaines)"
        weeks = re.findall(regex, date.strip().replace(" ", ""))[0][0]
        date_extracted = datetime.datetime.strptime(today, "%d/%m/%Y") - datetime.timedelta(days=int(weeks) * 7)
        return date_extracted

    return ""


# arrondissements = get_arrondissements()
# textfile = open("arrondissements_casablanca.txt", "w")
# for arrondissement in arrondissements:
#     print(arrondissement)
#     arrondissement = arrondissement.replace(" ", '-')
#     print(arrondissement)
#     textfile.write(arrondissement + "\n")
# textfile.close()

link_vendre = ["https://www.mubawab.ma/fr/crptd/casablanca-settat/" \
               "pr%C3%A9fecture-de-casablanca/casablanca/",
               "/immobilier-a-vendre"]
link_louer = ["https://www.mubawab.ma/fr/crptd/casablanca-settat/" \
               "pr%C3%A9fecture-de-casablanca/casablanca/",
               "/immobilier-a-louer"]
# get_offer_links(link_gen=link_louer)
get_data()
