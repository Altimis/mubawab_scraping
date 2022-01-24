import pandas as pd

import utils
from selenium.common.exceptions import NoSuchElementException
import re
from time import sleep
import random
import datetime
import pickle
import csv


def get_offer_links(driver: object = None, link_gen: object = None) -> object:
    """

    :param driver:
    :param link_gen:
    :return:
    """
    try:
        if not driver:
            driver = utils.init_driver(headless=True)
        utils.log_search_page(driver, link_gen)
        sleep(random.uniform(0.5, 1.5))
        # get the number of pages
        nb_element_text = driver.find_elements_by_class_name("sc-1cf7u6r-0")
        l = []
        for b in nb_element_text:
            page = b.text
            if page:
                try:
                    val = eval(str(page))
                except:
                    continue
                if type(val) == int:
                    l.append(eval(page))
        pages_nb = max(l)
        links = []
        for p in range(int(pages_nb)):
            post_link = str(link_gen) + "?o=" + str(p + 1)
            utils.log_search_page(driver, post_link)
            sleep(random.uniform(0.5, 1.5))
            i = 0
            while True:
                try:
                    link = driver.find_element_by_xpath(
                        '//div[@data-testid="adListCard' + str(i) + '"]/a').get_attribute(
                        'href')
                except:
                    break
                links.append(link)
                # sleep(random.uniform(0.5, 1.5))
                i += 1
            a_file = open("links_avito_appart_vente_casa.pkl", "wb")
            pickle.dump(links, a_file)
            a_file.close()
            print(f"{len(links)} saved.")
        return links
    except:
        a_file = open("links_avito_appart_vente_casa.pkl", "wb")
        pickle.dump(links, a_file)
        a_file.close()
        return links


def get_data(driver=None, links=None, links_path=None):
    """

    :param driver:
    :param links:
    :return:
    """
    if not driver:
        driver = utils.init_driver(headless=True)
    if not links:
        a_file = open(links_path, "rb")
        links = pickle.load(a_file)
    data = {"link": [], "title": [], "surface_totale": [], "surface_habitable": [], "chambre": [],
            "bain": [], "price": [], "ville": [], "time": [],
            "secteur": [], "type": [], "age": [], "etage": [], "salon": [], "description": [],
            "Concierge": [], "Balcon": [], "Terrasse": [], "Securite": [], "Parking": [], "Ascenseur": [],
            "Climatisation": [], "CuisineEquipee": [], "Garage": [], "Chauffage": [], "Piscine": [], "Jardin": [],
            "Titre": [], "Loti": [], "Duplex": [], "Meuble": []}
    # resume_nb = 361
    try:
        df = pd.read_csv("data_avito_apparts_vente_casa.csv")
        resume_nb = len(df.index) + 1
    except Exception as e:
        print(e)
        with open("data_avito_apparts_vente_casa.csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())
            resume_nb = 0
    print(f"scraping from {resume_nb} to {len(links)} ...")
    with open("data_avito_apparts_vente_casa.csv", 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i, link in enumerate(links):
            if i <= resume_nb:
                continue
            utils.log_search_page(driver, link)
            sleep(random.uniform(0.5, 0.75))
            major_elem = driver.find_elements_by_xpath('//span[contains(@class,"sc-1x0vz2r-0")]')
            price_element = driver.find_elements_by_xpath('//p[contains(@class,"sc-1x0vz2r-0")]')
            description_xpath = '//div[contains(@class,"sc-1g3sn3w-11")]'
            # first infos
            data['link'].append(link)
            title = get_title(driver)
            data["title"].append(title)
            surface_totale = get_surface(driver, major_elem)
            data['surface_totale'].append(surface_totale)
            chambre = get_chambres(driver)
            data['chambre'].append(chambre)
            bain = get_bains(driver)
            data['bain'].append(bain)
            price = get_price(price_element)
            data['price'].append(price)
            ville = get_ville(major_elem)
            data['ville'].append(ville)
            time = get_time(major_elem)
            data['time'].append(time)
            surface_habitable = look_next_el(major_elem, 'Surface habitable')
            data['surface_habitable'].append(surface_habitable)
            secteur = look_next_el(major_elem, "Secteur")
            data['secteur'].append(secteur)
            type = look_next_el(major_elem, "Type")
            data['type'].append(type)
            age = look_next_el(major_elem, "Âge du bien")
            data['age'].append(age)
            etage = look_next_el(major_elem, "Étage")
            data['etage'].append(etage)
            salon = look_next_el(major_elem, "Salons")
            data['salon'].append(salon)
            # desc
            description = get_description(driver, description_xpath)
            data['description'].append(description)
            # supp
            Concierge = get_txt_b_aria_labelledby(driver, "ConciergeTitleID")
            data['Concierge'].append(Concierge)
            Balcon = get_txt_b_aria_labelledby(driver, "BalconTitleID")
            data['Balcon'].append(Balcon)
            Terrasse = get_txt_b_aria_labelledby(driver, "TerrasseTitleID")
            data['Terrasse'].append(Terrasse)
            Securite = get_txt_b_aria_labelledby(driver, "SecuriteTitleID")
            data['Securite'].append(Securite)
            Parking = get_txt_b_aria_labelledby(driver, "ParkingTitleID")
            data['Parking'].append(Parking)
            Ascenseur = get_txt_b_aria_labelledby(driver, "AscenseurTitleID")
            data['Ascenseur'].append(Ascenseur)
            Climatisation = get_txt_b_aria_labelledby(driver, "ClimatisationTitleID")
            data['Climatisation'].append(Climatisation)
            CuisineEquipee = get_txt_b_aria_labelledby(driver, "CuisineEquipeeTitleID")
            data['CuisineEquipee'].append(CuisineEquipee)
            Garage = get_txt_b_aria_labelledby(driver, "GarageTitleID")
            data['Garage'].append(Garage)
            Chauffage = get_txt_b_aria_labelledby(driver, "ChauffageTitleID")
            data['Chauffage'].append(Chauffage)
            Piscine = get_txt_b_aria_labelledby(driver, "PiscineTitleID")
            data['Piscine'].append(Piscine)
            Jardin = get_txt_b_aria_labelledby(driver, "JardinTitleID")
            data['Jardin'].append(Jardin)
            Titre = get_txt_b_aria_labelledby(driver, "TitreTitleID")
            data['Titre'].append(Titre)
            Loti = get_txt_b_aria_labelledby(driver, "LotiTitleID")
            data['Loti'].append(Loti)
            Duplex = get_txt_b_aria_labelledby(driver, "DuplexTitleID")
            data['Duplex'].append(Duplex)
            Meuble = get_txt_b_aria_labelledby(driver, "MeubleTitleID")
            data['Meuble'].append(Meuble)

            data_to_add = (link, title, surface_totale, surface_habitable, chambre, bain, price, ville, time,
                           secteur, type, age, etage, salon, description, Concierge,
                           Balcon, Terrasse, Securite, Parking, Ascenseur, Climatisation, CuisineEquipee, Garage,
                           Chauffage, Piscine, Jardin, Titre, Loti, Duplex, Meuble)
            writer.writerow(data_to_add)
            # if i % 5 == 0:
            #     df = pd.DataFrame(data)
            #     df.to_csv("data_avito_apparts_vente.csv")
            print(f'{len(data["link"])} data saved.')

def get_price(els):
    """

    :param els:
    :return:
    """
    for el in els:
        if 'DH' in str(el.text) or 'DHS' in str(el.text) or 'DHs' in str(el.text) or 'Dh' in str(
                el.text) or 'Dhs' in str(el.text):
            t = str(el.text).strip()
            t = ''.join(t.split())
            price = int(re.findall(f'\d+', t)[0])
            return price


def get_description(driver, xpath):
    """

    :return:
    """
    try:
        return driver.find_element_by_xpath(xpath).text
    except:
        return ""
def get_ville(els):
    """

    :param els:
    :return:
    """
    if len(els):
        els = [str(el.text) for el in els]
        return str(els[0])
    else:
        return ""


def get_time(els):
    """

    :param els:
    :return:
    """
    if not len(els):
        return ""
    els = [str(el.text) for el in els]
    d = str(els[1])
    today = datetime.date.today().strftime("%d/%m/%Y")
    if re.match(f'\d+\D\d+', d):
        day = today

    return d


def look_next_el(els, exp):
    """

    :param els:
    :param exp:
    :return:
    """
    if not len(els):
        return ""
    els = [str(el.text) for el in els]
    for i, el in enumerate(els):
        if exp in el:
            return els[i + 1]


def get_txt_b_aria_labelledby(driver, labelledby):
    """

    :param labelledby:
    :return:
    """
    try:
        c = driver.find_element_by_css_selector('[aria-labelledby=' + labelledby + ']').find_element_by_xpath(
            './/../span').text
        return 1
    except:
        return 0


def get_title(driver):
    """

    :return:
    """
    try:
        title = driver.find_element_by_xpath('//h1[contains(@class,"sc-1x0vz2r-0")]').text
    except:
        title = ""
    return title


def get_surface(driver, major_elem):
    """

    :param driver:
    :return:
    """
    try:
        m = driver.find_element_by_css_selector('[aria-labelledby="SurfaceTotaleTitleID"]').find_element_by_xpath(
            './/../span').text
    except:
        m = ""
    if not m:
        try:
            m = look_next_el(major_elem, "Surface totale")
        except:
            m = ""
    return m


def get_chambres(driver):
    """

    :param driver:
    :return:
    """
    try:
        c = driver.find_element_by_css_selector('[aria-labelledby="ChambresTitleID"]').find_element_by_xpath(
            './/../span').text
    except:
        c = ""
    return c


def get_bains(driver):
    """

    :param driver:
    :return:
    """
    try:
        bains = driver.find_element_by_css_selector('[aria-labelledby="SalleDeBainTitleID"]').find_element_by_xpath(
            './/../span').text
    except:
        bains = ""
    return bains


# get_offer_links(link_gen='https://www.avito.ma/fr/maroc/immobilier-%C3%A0_vendre')
# get_offer_links(link_gen='https://www.avito.ma/fr/casablanca/appartements-%C3%A0_vendre')
get_data(links_path="links_avito_appart_vente_casa.pkl")
