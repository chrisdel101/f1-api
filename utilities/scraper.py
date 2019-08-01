from utilities import endpoints
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


# manually add in dif sizes for imgs
# takes url and index to choose size from list
def _change_img_size(src, list_index):
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
def _driver_images(name):
    page = requests.get(endpoints.driver_endpoint(name), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    driver_info = soup.find(
        'figcaption', class_="driver-details")
    driver_dict = {}
    try:
        if soup.find(class_='driver-main-image') and soup.find(class_='driver-main-image').img:

            img_src = soup.find(class_='driver-main-image').img['src']
            # replace img size with custom size
            new_str = _change_img_size(img_src, 3)
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
        # print('DICT', driver_dict)
        return driver_dict
    except ValueError:
        return "An error occured creating driver images."


# scrape for driver datas - return dict
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
            print('v', v)
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


def scrape_all_team_names():
    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    ul_teams_list = soup.find('ul', {'class', 'teamindex-teamteasers'})
    li_team_list = ul_teams_list.find_all('li')
    teams_endpoint = []
    for team in li_team_list:
        if team.find('h2'):
            team_dict = {}
            name_slug = "".join(_slugify(team.find('h2').text).split())
            team_dict['name_slug'] = name_slug
            name = " ".join(team.find('h2').text.split())
            team_dict['name'] = name
            teams_endpoint.append(team_dict)
        # print("ENDPOINTS", teams_endpoint)
    return teams_endpoint


# team slug needs to be capitalized
def scrape_single_team_stats(team_slug):
    print('TS', endpoints.team_endpoint(team_slug))
    page = requests.get(endpoints.team_endpoint(team_slug), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    team_details = soup.find('section', {'class', 'stats'})
    details = ['Full Team Name',
               'Base',
               'Team Chief',
               'Technical Chief',
               'Chasis',
               'Power Unit',
               'First Team Entry',
               'Highest Race Finish',
               'Pole Positions',
               'Fastest Laps'
               ]
    team_dict = {}
    try:
        if team_details.find_all('tr'):
            # loop over html
            for team in team_details.find_all('tr'):
                # print('Team', team)
                # # loop over all wanted details
                for detail in details:
                    #     # if they match add to driver object
                    if team.span and team.span.text == detail:
                        team_dict[_slugify(team.span.text)
                                  ] = team.td.text
                        continue
        # print('TEAM', team_dict)
        return team_dict

    except ValueError:
        return "An error occured creating driver data."
