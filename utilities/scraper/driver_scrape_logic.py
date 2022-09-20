import logging
from utilities import endpoints
from bs4 import BeautifulSoup
import requests
import re
from user_agent import generate_user_agent
from slugify import Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'

headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}


# - scrape for driver images and other info -
# - return dict
def _driver_page_scrape(name):
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    return soup


# # manually add in dif sizes for imgs
# # takes url and index to choose size from list
def _change_driver_img_size(src, list_index):
    # replace scraped img size with one the sizes below
    regex = "image.img.[\d]+\.?.[\w]+"
    sizes = ['320', '640', '768', '1536']
    r = "image.img.{0}.medium".format(sizes[list_index])
    sub = re.sub(regex, r, src)
    return sub


# takes in hypenated name and strips leaving slug
def _extract_driver_name_slug_from_url(url):
    # revese the string
    rev = url[::-1]
    # match 2 hypens lmth.seirv-ed-kcyn/
    # & match 1 hypen lmth.seirv-ed-kcyn/
    regex3 = "^lmth\.([a-z]+\-[a-z]+\-[a-z]+|[a-z]+\-[a-z]+)"
    # return a list with reversed name
    extract = re.findall(regex3, rev)
    # check list len first
    if not len(extract):
        raise ValueError(
            'Error _extract_driver_name_slug_from_url: no list to index')
    # get list item and un-reverse
    name = extract[0][::-1]
    return name


# handle mutli part names, make single name with one comma - NOT USED
def _comma_seperate_driver_name(name):
    print('name', name)
    _list = name.split('\n')
    _str = ",".join(_list).strip(',').replace(" ", "")
    return _str


# return list of comma sep'd names
# can have more than 2 names - Nyck,De,Vries
def scrape_all_driver_names():
    page = requests.get(endpoints.drivers_endpoint(), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    drivers_list = soup.find(class_='drivers').ul
    drivers = []
    drivers_list = drivers_list.find_all('li')
    for driver in drivers_list:
        # remove whitespace
        d = ",".join(driver.text.split())
        drivers.append(d)
    return drivers


# extract names from standings, includes reserve drivers
def extract_all_drivers_names_from_standings(standings_list):
    driver_names = []
    for standing in standings_list:
        driver_names.append(standing['name_slug'])
    return driver_names


def scrape_all_drivers_standings():
    page = requests.get(endpoints.standings_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    standings_list = soup.find(class_='resultsarchive-table')
    rows = standings_list.find_all('tr')
    drivers = []
    for row in rows:
        #    find row with a tag - first valid row
        if row.find('a'):
            tds = row.find_all('td')
            # get url with name
            href = row.find('a')['href']
            # extract name slug
            name_slug = _extract_driver_name_slug_from_url(href)
            points = tds[5].text
            position = tds[1].text
            car = tds[4].text.strip()
            drivers.append(
                {
                    'name_slug': name_slug,
                    'points': points,
                    'standings_position': position,
                    'car': car
                }
            )
    return drivers


def get_main_image(name_slug):
    if type(name_slug) is not str:
        raise TypeError('get_main_img must take a string.')
    try:
        soup = _driver_page_scrape(name_slug)
        if soup.find(class_='driver-main-image') and soup.find(class_='driver-main-image').img:
            img_src = soup.find(class_='driver-main-image').img['src']
            # replace img size with custom size
            new_str = _change_driver_img_size(img_src, 3)
            main_image = "{0}/{1}".format(
                endpoints.home_endpoint(), new_str)
            return main_image
        else:
            logging.warning("Warning: No main image for driver found.")

    except Exception as e:
        logging.error('An error in driver main_image %s', e)


def get_driver_name(name_slug):
    if type(name_slug) is not str:
        raise TypeError('get_driver_name must take a string.')
    try:
        soup = _driver_page_scrape(name_slug)
        driver_info = soup.find(
            'figcaption', class_="driver-details")
        if driver_info.find('h1', {"class", "driver-name"}):
            driver_name = driver_info.find(
                'h1', {"class", "driver-name"}).text
            return driver_name.strip()
        else:
            logging.warning("Warning: No name for driver found.")
    except Exception as e:
        logging.error("An error in getting driver name %s", e)


def get_driver_number(name_slug):
    if type(name_slug) is not str:
        raise TypeError('get_driver_number must take a string.')
    try:
        soup = _driver_page_scrape(name_slug)
        driver_info = soup.find(
            'figcaption', class_="driver-details")
        if driver_info.find('div', {'class', 'driver-number'}):
            driver_number = driver_info.find(
                'div', {'class', 'driver-number'}).span.text
            return driver_number
        else:
            logging.warning("Warning: No number for driver found.")
    except Exception as e:
        logging.error("An error on getting driver number %s", e)


def get_driver_flag(name_slug):
    if type(name_slug) is not str:
        raise TypeError('get_driver_flag must take a string.')
    try:
        soup = _driver_page_scrape(name_slug)
        driver_info = soup.find(
            'figcaption', class_="driver-details")
        if driver_info.find('span', {'class', 'icn-flag'}) and driver_info.find('span', {'class', 'icn-flag'}).img.has_attr('src'):
            flag_img_url = driver_info.find(
                'span', {'class', 'icn-flag'}).img['src']
            return "{0}/{1}".format(endpoints.home_endpoint(), flag_img_url)
        else:
            logging.warning("Warning: No flag-icon for driver found.")
    except Exception as e:
        logging.error("An error in getting driver flag %s", e)


def scrape_driver_details(name_slug):
    if type(name_slug) is not str:
        raise TypeError('scrape_driver_details must take a string.')
    soup = _driver_page_scrape(name_slug)
    driver_details = soup.find(class_='driver-details')
    details = ['Team',
               'Country',
               'Podiums',
               'Points',
               'Grands Prix entered',
               'World Championships',
               'Highest race finish',
               'Highest race finish',
               'Highest grid position',
               'Date of birth',
               'Place of birth',
               ]
    # if len is more than zero then added unknown markup changes
    unknown_attr = []
    driver_dict = {}
    try:
        if driver_details and driver_details.find_all('tr'):
            # loop over html
            for driver in driver_details.find_all('tr'):
                # loop over all wanted details
                found = False
                for i, detail in enumerate(details):
                    # if they match add to driver object
                    if driver.span and driver.span.text == detail:

                        driver_dict[
                            _slugify(driver.span.text)
                        ] = driver.td.text
                        found = True
                        # del item so not loop over again
                        del details[i]
                        break
                if not found:
                    print("Warning: match not found", detail)
                    unknown_attr.appped(detail)
        # add any unknown attributes to add later
        return {
            0: unknown_attr,
            1: driver_dict
        }
    except Exception as e:
        logging.error("An error occured creating driver data. %s", e)
        return("An error occured creating driver data.", e)


def scrape_driver_stats(name_slug):
    if type(name_slug) is not str:
        raise TypeError('scrape_driver_stats must take a string.')
    driver_dict = {}
    try:
        for key, value in scrape_driver_details(name_slug)[1].items():
            driver_dict[key] = value
        return driver_dict
    except Exception as e:
        logging.error("Error in apply_scraper_set1_complete_drive.%s", e)
        return('Error in apply_scraper_set1_complete_driver', e)
