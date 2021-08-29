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


def _extract_name_from_url(url):
    # revese the string
    rev = url[::-1]
    regex = "^lmth\.[a-z]+\-[a-z]+\/"
    ex = re.findall(regex, rev)
    # remove first chars
    name = ex[0][5:]
    # remove trailing / and reverse
    name = name[:-1][::-1]
    return name


# - scrape all drivers names of the page -
# - return list
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


def scrape_all_drivers_standings():
    page = requests.get(endpoints.standings_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    standings_list = soup.find(class_='resultsarchive-table')
    rows = standings_list.find_all('tr')
    drivers = []
    for row in rows:
        if row.find('a'):
            # get url with name
            href = row.find('a')['href']
            # extract name slug
            name_slug = _extract_name_from_url(href)
            points = row.find('td', {'class', 'bold'}).text
            position = row.find('td', {'class', 'dark'}).text
            drivers.append(
                {
                    'name_slug': name_slug,
                    'points': points,
                    'standings_position': position
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
            print("Warning: No main image for driver found.")

    except Exception as e:
        print('An error in driver main_image', e)


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


def scrape_driver_details_func1(name_slug):
    if type(name_slug) is not str:
        raise TypeError('scrape_driver_details_func1 must take a string.')
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
        # add any unknown attributes to add later
        return {
            0: unknown_attr,
            1: driver_dict
        }
    except Exception as e:
        return("An error occured creating driver data.", e)


def scrape_driver_stats(name_slug):
    if type(name_slug) is not str:
        raise TypeError('get_complete_driver_data must take a string.')
    driver_dict = {}
    try:
        for key, value in scrape_driver_details_func1(name_slug)[1].items():
            driver_dict[key] = value
        return driver_dict
    except Exception as e:
        return('Error in apply_scraper_set1_complete_driver', e)


def apply_scraper_func2_complete_driver(name_slug, driver_dict):
    try:
        driver_dict['main_image'] = get_main_image(name_slug)
        driver_dict['driver_name'] = get_driver_name(name_slug)
        driver_dict['driver_number'] = get_driver_number(name_slug)
        driver_dict['flag_img_url'] = get_driver_flag(name_slug)
        return driver_dict
    except Exception as e:
        return('Error in apply_scraper_set2_complete_driver', e)
