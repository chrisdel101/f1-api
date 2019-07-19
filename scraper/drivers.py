from scraper import endpoints, utils

from bs4 import BeautifulSoup
import requests
from user_agent import generate_user_agent

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
    return {
        'main_image': "{0}/{1}".format(endpoints.home_endpoint(), soup.find(class_='driver-main-image').img['src']),
        'name': driver_info.h1.string,
        'number': driver_info.find('span').string,
        'flag_img_url': driver_info.find_all('img')[0]['src']
    }


def driver_stats(name):
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    driver_details = soup.find(class_='driver-details')
    driver_stats = driver_details.find_all('tr')[8].td.string
    images = _driver_images(name)
    return {
        'main_image': images['main_image'],
        'name': images['name'],
        'number': images['number'],
        'flag_img_url': images['flag_img_url'],
        'team': driver_details.find_all('tr')[0].td.string,
        'country': driver_details.find_all('tr')[1].td.string,
        'podiums': driver_details.find_all('tr')[2].td.string,
        'points': driver_details.find_all('tr')[3].td.string,
        'grand_prix_entered': driver_details.find_all('tr')[4].td.string,
        'world_championships': driver_details.find_all('tr')[5].td.string,
        'highest_finish': driver_details.find_all('tr')[6].td.string,
        'highest_grid_position': driver_details.find_all('tr')[7].td.string,
        'DOB': driver_details.find_all('tr')[8].td.string,
        'place_of_birth': driver_details.find_all('tr')[8].td.string
    }
