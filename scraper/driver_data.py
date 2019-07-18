from scraper import endpoints
from bs4 import BeautifulSoup
import requests


def driver_stats(name):
    page = requests.get(endpoints.driver_endpoint(name))
    soup = BeautifulSoup(page.text, 'html.parser')
    driver_details = soup.find(class_='driver-details')
    driver_stats = driver_details.find_all('tr')[8].td.string
    return {
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


def driver_name_flag_number(name):
    page = requests.get(endpoints.driver_endpoint(name))
    soup = BeautifulSoup(page.text, 'html.parser')
    driver_info = soup.find(
        'figcaption', class_="driver-details")
    return {
        'name': driver_info.h1.string,
        'number': driver_info.find('span').string,
        'flag_img_url': driver_info.find_all('img')[0]['src']
    }


# print(driver_endpoint('lewis-hamilton'))
