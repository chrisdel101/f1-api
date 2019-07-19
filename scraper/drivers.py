from scraper import endpoints, utils
from bs4 import BeautifulSoup
import requests
from user_agent import generate_user_agent
from slugify import slugify, Slugify
_slugify = Slugify(to_lower=True)


headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}


def list_all_drivers():
    page = requests.get(endpoints.drivers_endpoint(), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    drivers_list = soup.find(class_='drivers').ul
    drivers = []
    drivers_list = drivers_list.find_all('li')
    text = drivers_list[0].text
    # name = utils.extract_name_whitespace(drivers_list[0].text)
    for driver in drivers_list:
        d = ",".join(driver.text.split())
        drivers.append(d)
    # print(drivers)
    return drivers


def _driver_images(name):
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    driver_info = soup.find(
        'figcaption', class_="driver-details")
    driver_images = {}
    try:
        if soup.find(class_='driver-main-image') and soup.find(class_='driver-main-image').img:
            driver_images['main_image'] = "{0}/{1}".format(
                endpoints.home_endpoint(), soup.find(class_='driver-main-image').img['src'])
        else:
            print("Error: No main image for driver found.")

        if driver_info.find('h1', {"class", "driver-name"}):
            driver_images['driver_name'] = driver_info.find(
                'h1', {"class", "driver-name"}).text
        else:
            print("Error: No name for driver found.")

        if driver_info.find('div', {'class', 'driver-number'}):
            driver_images['driver_number'] = driver_info.find(
                'div', {'class', 'driver-number'}).span.text
        else:
            print("Error: No number for driver found.")

            print("Error: No number for driver found.")
        if driver_info.find('span', {'class', 'icn-flag'}) and driver_info.find(
                'span', {'class', 'icn-flag'}).img.has_attr('src'):
            driver_images['flag_img_url'] = driver_info.find(
                'span', {'class', 'icn-flag'}).img['src']
        else:
            print("Error: No flag-icon for driver found.")
            # print(driver_info.h1.has_class("driver-name"))
            # return {
            #     'main_image': "{0}/{1}".format(endpoints.home_endpoint(), soup.find(class_='driver-main-image').img['src']),
            #     'name': driver_info.h1.string,
            #     'number': driver_info.find('span').string,
            #     'flag_img_url': driver_info.find_all('img')[0]['src']
            #
        return driver_images
    except ValueError:
        return "An error occured creating driver images."


def driver_stats(name):
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
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
    _driver_images(name)
    try:
        for _, (k, v) in enumerate(_driver_images(name).items()):
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
        # 'main_image': images['main_image'],
        # 'name': images['name'],
        # 'number': images['number'],
