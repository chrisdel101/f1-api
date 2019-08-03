from utilities import endpoints, utils
from bs4 import BeautifulSoup, UnicodeDammit
import requests
import re
from user_agent import generate_user_agent
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'

headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}


# # manually add in dif sizes for imgs
# # takes url and index to choose size from list
def _change_driver_img_size(src, list_index):
    # replace scraped img size with one the sizes below
    regex = "image.img.[\d]+\.?.[\w]+"
    sizes = ['320', '640', '768', '1536']
    r = "image.img.{0}.medium".format(sizes[list_index])
    sub = re.sub(regex, r, src)
    return sub


# - scrape all drivers names of the page -
# - return list
def scrape_all_driver_names():
    page = requests.get(endpoints.drivers_endpoint(), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    drivers_list = soup.find(class_='drivers').ul
    drivers = []
    drivers_list = drivers_list.find_all('li')
    text = drivers_list[0].text
    for driver in drivers_list:
        # remove whitespace
        d = ",".join(driver.text.split())
        drivers.append(d)
    return drivers


# - scrape for driver images and other info -
# - return dict
def _driver_page_scrape(name):
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    return soup


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
            print("Warning: No main image for driver found.")

    except Exception as e:
        print('An error in main_image', e)


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
            return driver_name
        else:
            print("Warning: No name for driver found.")
    except Exception as e:
        print("An error in getting driver name", e)


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
            print("Warning: No number for driver found.")
    except Exception as e:
        print("An error on getting driver number", e)


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
            print("Warning: No flag-icon for driver found.")
    except Exception as e:
        print("An error in getting driver flag", e)


def scrape_driver_details(name_slug):
    soup = _driver_page_scrape(name_slug)
    driver_details = soup.find(class_='driver-details')
    details = ['Team',
               'Country',
               'Podiums',
               'Points',
               'Grands Prix entered',
               'World Championships',
               'Highest race finish',
               'Highest grid position',
               'Date of birth',
               'Place of birth',
               ]
    # if len is more than zero then added unknown markup changes
    unknown_attr = []
    driver_dict = {}
    try:
        if driver_details.find_all('tr'):
            # loop over html
            for driver in driver_details.find_all('tr'):
                # loop over all wanted details
                found = False
                for i, detail in enumerate(details):
                    # if they match add to driver object
                    if driver.span and driver.span.text == detail:
                        driver_dict[_slugify(driver.span.text)
                                    ] = driver.td.text
                        found = True
                        # del item so not loop over again
                        del details[i]
                        break
                if not found:
                    print("Warning: match not found", detail)
                    unknown_attr.appped(detail)
        return {
            0: unknown_attr,
            1: driver_dict
        }
    except Exception as e:
        return("An error occured creating driver data.", e)


def scrape_single_driver_stats(name_slug):
    page = requests.get(endpoints.driver_endpoint(name_slug), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    driver_details = soup.find(class_='driver-details')
    details = ['Team',
               'Country',
               'Podiums',
               'Points',
               'Grand Prix entered',
               'World Championships',
               'Higest race finish',
               'Highest grid position',
               'Date of birth',
               'Place of birth'
               ]
    driver_dict = {}
    _driver_images(name_slug)
    try:
        # loop in other outside values to driver_dict
        for _, (k, v) in enumerate(_driver_images(name_slug).items()):
            driver_dict[k] = v
    except ValueError:
        return "An error occured unpacking driver images"
    # error checking
    try:
        if driver_details.find_all('tr'):
            # loop over html
            for driver in driver_details.find_all('tr'):
                # loop over all wanted details
                for detail in details:
                    # if they match add to driver object
                    if driver.span and driver.span.text == detail:
                        driver_dict[_slugify(driver.span.text)
                                    ] = driver.td.text
                        continue
            return driver_dict
    except ValueError:
        return "An error occured creating driver data."
