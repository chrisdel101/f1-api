from bs4 import BeautifulSoup
import requests
import os

from utilities import endpoints, utils
from user_agent import generate_user_agent
from slugify import Slugify
import re
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'

headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}


def _team_page_scrape():
    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    return soup


# manually add in dif sizes for imgs
# takes url and index to choose size from list
def _change_team_img_size(src, list_index):
    # replace scraped img size with one the sizes below
    regex = "(image[\\d]+x[\\d]+|image[\\d]+)\\.img\\.[\\d]+\\.(medium|large|small)"
    sizes = ['320', '640', '768', '1536']
    r = "image1.img.{0}.medium".format(sizes[list_index])
    sub = re.sub(regex, r, src)
    if os.environ['LOGS'] != 'off':
        if src == sub:
            print('_change_team_img_size: DIMS not changed')
         # get team id from team lookup
    return sub

# scrape all team names - returns a list of dicts


def scrape_all_team_names():
    soup = _team_page_scrape()
    # get all divs will teams as children
    teams_list_markup = soup.find_all('div', {'class', 'name'})
    teams_endpoint = []
    for team in teams_list_markup:
        if team.contents:
            # index for span with name
            name_span = team.contents[3]
            team_dict = {}
            name_slug = "".join(_slugify(name_span.text).split())
            team_dict['name_slug'] = name_slug
            team_name = " ".join(name_span.text.split())
            team_dict['team_name'] = team_name
            teams_endpoint.append(team_dict)

    if os.environ['LOGS'] != 'off':
        print("logging TEAM NAMES", teams_endpoint)
    return teams_endpoint


# takes in team_name_header returns url
def get_main_image(team_name_header):
    if not team_name_header:
        return ValueError('get_main_image missing input')
    # get particular team endpint with team_name_header
    page = requests.get(endpoints.team_endpoint(
        team_name_header), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    # find main team img
    carousel = soup.find('section', {'class', 'main-gallery'})
    if carousel:
        # take first image available, get src
        main_img_src = carousel.find(
            'img')['src']
        # resize img b/c scrape is wrong
        main_img_src = _change_team_img_size(main_img_src, 3)
        # form into full URL
        main_img_url = "{0}/{1}".format(
            endpoints.home_endpoint(), main_img_src)
        return main_img_url
    else:
        print("Warning: No main_img found")
        return ''


def get_all_images(team_name_header):
    if not team_name_header:
        return ValueError('get_main_image missing input')
    # get particular team endpint with team_name_header
    page = requests.get(endpoints.team_endpoint(
        team_name_header), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    # find main team img
    image_list = soup.find(
        'section', {'class', 'main-gallery'}).findAll('img')
    imgs_urls = [img['src'] for img in image_list]
    return imgs_urls


# team_name_header is capped
def get_main_logo_url(team_name_header):
    if not team_name_header:
        return ValueError('get_main_logo_url missing input')
    # get particular team endpint with slug
    page = requests.get(endpoints.team_endpoint(
        team_name_header), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    # get stats_container
    stats_container = soup.find('section', {'class', 'stats'})
    if stats_container:
        # find img src
        img_src = stats_container.find(
            'div', {'class', 'brand-logo'}).find('img')['src']
        # combine into proper endpoint
        logo_url = "{0}/{1}".format(
            endpoints.home_endpoint(), img_src)
        return logo_url
    else:
        print('Warning: No logo_img found.')
        return ''


# uses team name, not team_full_name
def get_small_logo_url(team_name):
    if not team_name:
        return ValueError('get_small_logo_url missing input')
    # get particular all teams endpint, no slug
    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    teams_container = soup.find(
        'div', {'class', 'team-listing'}).find('div', {'class', 'row'}).find_all('div', {'class', 'col-12'})
    if teams_container:
        for team in teams_container:
            find_team_name = team.find(
                'div', {'class', 'name'}).contents[3].text

            if find_team_name == team_name:
                small_logo = team.find(
                    'div', {'class', 'logo'}).find('img')['data-src']
                return small_logo
    else:
        print('Warning: No logo_img found.')
        return ''


def get_drivers(team_name_header):
    if not team_name_header:
        return ValueError('get_drivers missing input')
    page = requests.get(endpoints.team_endpoint(
        team_name_header), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    drivers_list = soup.find('ul', {'class', 'drivers'})
    if drivers_list:
        # locate driver markup, scrape names
        driver1_name = drivers_list.find_all('li')[0].find(
            'h1', {'class', 'driver-name'}).text
        driver2_name = drivers_list.find_all('li')[1].find(
            'h1', {'class', 'driver-name'}).text
        # form into usable list
        drivers_list = utils.create_driver_list([driver1_name, driver2_name])
        # attach to obj
        return drivers_list
    else:
        print('No drivers list found in get_drivers')
        return ''

# team slug needs to be capitalized


def scrape_single_team_stats(team_name_header, stats_to_scrape):
    # manually cap first letter
    page = requests.get(endpoints.team_endpoint(
        team_name_header), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    team_details = soup.find('section', {'class', 'stats'})
    team_dict = {}
    try:
        if team_details.find_all('tr'):
            # loop over html
            for team in team_details.find_all('tr'):
                # # loop over all wanted details
                for stat in stats_to_scrape:
                    #     # if they match add to team object
                    if team.span and team.span.text == stat:
                        team_dict[_slugify(team.span.text)
                                  ] = team.td.text
                        continue
        return team_dict

    except ValueError:
        return "An error occured creating driver data."
