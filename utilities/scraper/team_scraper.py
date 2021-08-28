from controllers import drivers_controller, teams_controller
from bs4 import BeautifulSoup
import requests
import os

from user_agent.base import USER_AGENT_TEMPLATE
from utilities import endpoints, utils
from user_agent import generate_user_agent
from slugify import slugify, Slugify
import sys
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
    regex = "image[\d]+.img.[\d]+.(medium|small|large)"
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
            name = " ".join(name_span.text.split())
            team_dict['name'] = name
            teams_endpoint.append(team_dict)

    if os.environ['LOGS'] != 'off':
        print("TEAM NAMES", teams_endpoint)
    return teams_endpoint


# takes in dict, adds main img then returns dict
def get_main_image(scraper_dict, url_name_slug, force_overwrite=False):
    # get particular team endpint with slug
    page = requests.get(endpoints.team_endpoint(
        url_name_slug), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_main_image must take a dict.')
    if 'main_image' in scraper_dict and not force_overwrite:
        # return unchanged dict if already there
        return scraper_dict
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
        # add to dict
        scraper_dict['main_image'] = main_img_url
        return scraper_dict
    else:
        print("Warning: No main_img found")
        return scraper_dict


def get_main_logo_url(scraper_dict, url_name_slug, force_overwrite=False):
    # get particular team endpint with slug
    page = requests.get(endpoints.team_endpoint(
        url_name_slug), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_main_logo_url must take a dict.')
    if 'logo_url' in scraper_dict and not force_overwrite:
        # return unchanged dict
        return scraper_dict
    # get stats_container
    stats_container = soup.find('section', {'class', 'stats'})
    if stats_container:
        # find img src
        img_src = stats_container.find(
            'div', {'class', 'brand-logo'}).find('img')['src']
        # combine into proper endpoint
        logo_url = "{0}/{1}".format(
            endpoints.home_endpoint(), img_src)
        # add to dict
        scraper_dict['main_logo_url'] = logo_url
        return scraper_dict
    else:
        print('Warning: No logo_img found.')
        return scraper_dict


def get_small_logo_url(scraper_dict, short_team_name, force_overwrite=False):
    # get particular all teams endpint, no slug
    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_small_logo_url must take a dict.')
    if 'get_small_logo_url' in scraper_dict and not force_overwrite:
        # return unchanged dict
        return scraper_dict
    # get stats_container
    teams_container = soup.find(
        'div', {'class', 'team-listing'}).find('div', {'class', 'row'}).find_all('div', {'class', 'col-12'})
    if teams_container:
        for team in teams_container:
            team_name = team.find('div', {'class', 'name'}).contents[3].text
            if team_name == short_team_name:
                small_logo = team.find(
                    'div', {'class', 'logo'}).find('img')
                scraper_dict['small_logo'] = small_logo

    else:
        print('Warning: No logo_img found.')
    return scraper_dict


def get_drivers(scraper_dict, url_name_slug, force_overwrite=False):
    page = requests.get(endpoints.team_endpoint(
        url_name_slug), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_drivers must take a dict.')
    if 'drivers' in scraper_dict and not force_overwrite:
        # return unchanged dict
        return scraper_dict
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
        scraper_dict['drivers'] = drivers_list
    else:
        print('No drivers list found in get_drivers')
    return scraper_dict


def add_imgs_markup(scraper_dict):
    if os.environ['LOGS'] != 'off':
        print('\n')
        print('Change DICT', scraper_dict)
    if type(scraper_dict) is not dict:
        return
    url_name_slug = scraper_dict['url_name_slug']
    try:
        # if team.contents:
        if os.environ['LOGS'] != 'off':
            if os.environ['FLASK_ENV'] == 'development':
                print('url_name_slug', url_name_slug)
        # - call each function to get additional markup
            scraper_dict = get_main_image(
                scraper_dict, url_name_slug, True)
            scraper_dict = get_main_logo_url(scraper_dict, url_name_slug, True)
            scraper_dict = get_small_logo_url(
                scraper_dict, scraper_dict['name'], True)
            scraper_dict = get_drivers(scraper_dict, url_name_slug)
        return scraper_dict

    except Exception as e:
        print('error in team_iterator', e)


# team slug needs to be capitalized
def scrape_single_team_stats(team_slug):
    # print('TS', endpoints.team_endpoint(team_slug))
    page = requests.get(endpoints.team_endpoint(team_slug), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    team_details = soup.find('section', {'class', 'stats'})
    details = ['Full Team Name',
               'Base',
               'Team Chief',
               'Technical Chief',
               'Chasis',
               'Power Unit',
               'First Team Entry',
               'World Championships',
               'Highest Race Finish',
               'Pole Positions',
               'Fastest Laps',
               ]
    team_dict = {}
    try:
        if team_details.find_all('tr'):
                # loop over html
            for team in team_details.find_all('tr'):
                    # print('Team', team)
                    # # loop over all wanted details
                for detail in details:
                        #     # if they match add to team object
                    if team.span and team.span.text == detail:
                        team_dict[_slugify(team.span.text)
                                  ] = team.td.text
                        continue
        return team_dict

    except ValueError:
        return "An error occured creating driver data."
