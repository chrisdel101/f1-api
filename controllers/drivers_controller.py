import re
from user_agent import generate_user_agent
import requests
from bs4 import BeautifulSoup
from slugify import slugify, Slugify
import endpoints
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'

headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}


# manually add in dif sizes for imgs
# takes url and index to choose size from list
def change_img_size(src, list_index):
    # replace scraped img size with one the sizes below
    regex = "image.img.[\d]+\.?.[\w]+"
    sizes = ['320', '640', '768', '1536']
    r = "image.img.{0}.medium".format(sizes[list_index])
    sub = re.sub(regex, r, src)
    return sub


def list_all_drivers():
    # - scrape all drivers names of the page -
    # - return list
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


def _driver_images(name):
    # - scrape for driver images and other info -
    # - return dict
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    print('====', page)
    soup = BeautifulSoup(page.text, 'html.parser')
    driver_info = soup.find(
        'figcaption', class_="driver-details")
    driver_dict = {}
    try:
        if soup.find(class_='driver-main-image') and soup.find(class_='driver-main-image').img:

            img_src = soup.find(class_='driver-main-image').img['src']
            # replace img size with custom size
            new_str = change_img_size(img_src, 3)
            driver_dict['main_image'] = "{0}/{1}".format(
                endpoints.home_endpoint(), new_str)

        else:
            print("Error: No main image for driver found.")

        if driver_info.find('h1', {"class", "driver-name"}):
            driver_dict['driver_name'] = driver_info.find(
                'h1', {"class", "driver-name"}).text
        else:
            print("Error: No name for driver found.")

        if driver_info.find('div', {'class', 'driver-number'}):
            driver_dict['driver_number'] = driver_info.find(
                'div', {'class', 'driver-number'}).span.text
        else:
            print("Error: No number for driver found.")

        if driver_info.find('span', {'class', 'icn-flag'}) and driver_info.find(
                'span', {'class', 'icn-flag'}).img.has_attr('src'):
            driver_dict['flag_img_url'] = driver_info.find(
                'span', {'class', 'icn-flag'}).img['src']
        else:
            print("Error: No flag-icon for driver found.")
        return driver_dict
    except ValueError:
        return "An error occured creating driver images."


def driver_stats(name):
    # scrape for driver datas - return dict
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    print("====", name)
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
        # loop in other outside values to driver_dict
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
                # add driver slug
            driver_dict['name_slug'] = slugify(
                driver_dict['driver_name']).lower()
            return driver_dict
    except ValueError:
        return "An error occured creating driver data."
