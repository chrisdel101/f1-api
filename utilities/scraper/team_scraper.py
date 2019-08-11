from bs4 import BeautifulSoup
import requests
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
    regex = "image[\d]+x[\d]+.img.[\d]+.(medium|small|large)"
    sizes = ['320', '640', '768', '1536']
    r = "image16x9.img.{0}.medium".format(sizes[list_index])
    sub = re.sub(regex, r, src)
    return sub


def scrape_all_team_names():
    soup = _team_page_scrape()
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


def get_main_image(scraper_dict, li, url_name_slug):
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_main_image must take a dict.')
    if 'main_image' in scraper_dict:
        # return unchanged dict
        return scraper_dict
        # find main team img
    if li.find('div', {'class', 'teamteaser-image'}) and li.find('div', {'class', 'teamteaser-image'}).find('img'):
        main_img_src = li.find(
            'div', {'class', 'teamteaser-image'}).find('img')['src']
        # resize img
        main_img_src = _change_team_img_size(main_img_src, 3)
        main_img = "{0}/{1}".format(
            endpoints.home_endpoint(), main_img_src)
        # if slug param matches slug of scraperx_dict-
        # - attach main_img to current team
        if scraper_dict['url_name_slug'] == url_name_slug:
            scraper_dict['main_image'] = main_img
        return scraper_dict
    else:
        print("Warning: No main_img found")
        return scaper_dict


def get_flag_img_url(scraper_dict, li, url_name_slug):
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_flag_img_url must take a dict.')
    if 'flag_img_url' in scraper_dict:
        # return unchanged dict
        return scraper_dict
    if li.find('span', {'class', 'teamteaser-flag'}):
        l = li.find('span', {'class', 'teamteaser-flag'})
        if(l.find('img')):
            if scraper_dict['url_name_slug'] == url_name_slug:
                flag_src = li.find('img')['src']
                flag_img = "{0}/{1}".format(
                    endpoints.home_endpoint(), flag_src)
                scraper_dict['flag_img_url'] = flag_img
        return scraper_dict
    else:
        print('Warning: No flag_img found.')
        return scraper_dict


def get_logo_url(scraper_dict, li, url_name_slug):
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_logo_url must take a dict.')
    if 'logo_url' in scraper_dict:
        # return unchanged dict
        return scraper_dict
    if li.find('div', {'class', 'teamteaser-sponsor'}):
        if scraper_dict['url_name_slug'] == url_name_slug:
            l = li.find('div', {'class', 'teamteaser-sponsor'})
            if l.find('img'):
                logo_src = l.find('img')['src']
                logo_img = "{0}/{1}".format(
                    endpoints.home_endpoint(), logo_src)
                scraper_dict['logo_url'] = logo_img
        return scraper_dict
    else:
        print('Warning: No logo_img found.')
        return scraper_dict


def get_podium_finishes(scraper_dict, li, url_name_slug):
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_podium_finishes must take a dict.')
    if 'podium_finishes' in scraper_dict:
        # return unchanged dict
        return scraper_dict
    if li.find('table', {'class', 'stat-list'}):
        if scraper_dict['url_name_slug'] == url_name_slug:
            t = li.find('table', {'class', 'stat-list'})
            if t.find_all('td', {'class', 'stat-value'})[0].text:
                scraper_dict['podium_finishes'] = t.find(
                    'td', {'class', 'stat-value'}).text
        return scraper_dict
    else:
        print('Warning: No podium_finishes found.')
        return scraper_dict


def get_championship_titles(scraper_dict, li, url_name_slug):
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_championship_titles must take a dict.')
        # if already there return
    if 'championship_titles' in scraper_dict:
        # return unchanged dict
        return scraper_dict
    if li.find('table', {'class', 'stat-list'}):
        if scraper_dict['url_name_slug'] == url_name_slug:
            t = li.find('table', {'class', 'stat-list'})
            if t.find_all('td', {'class', 'stat-value'})[1].text:
                scraper_dict['championship_titles'] = t.find_all(
                    'td', {'class', 'stat-value'})[1].text
        # print('SC', scraper_dict)
        return scraper_dict
    else:
        print('Warning: No championship_titles found.')
        return scraper_dict


def get_drivers(scraper_dict, li, url_name_slug):
    if type(scraper_dict) is not dict:
        ValueError('Warning: get_drivers must take a dict.')
    if 'drivers' in scraper_dict:
        # return unchanged dict
        return scraper_dict
    if li.find('ul', {'class', 'teamteaser-drivers'}):
        if scraper_dict['url_name_slug'] == url_name_slug:
            ul = li.find('ul', {'class', 'teamteaser-drivers'})
            drivers = ul.find_all('li')
            if len(drivers) > 0:
                drivers = [drivers[0].text, drivers[1].text]
                scraper_dict['drivers'] = drivers
        return scraper_dict
    else:
        print('Warning: No drivers found.')
        return scraper_dict


def iterate_teams_markup(scraper_dict):
    print('\n')
    print('Change DICT', scraper_dict)
    if type(scraper_dict) is not dict:
        return
    try:
        soup = _team_page_scrape()
        all_teams = soup.find('ul', {'class', 'teamindex-teamteasers'})
        # loop over all teams on the page
        # if match scraper_dict team_name to list li
        for li in all_teams.find_all('li'):
            if li.find('a'):

                # # strip all text to get matching url_name_slug
                team_name = li.find('a')['href']
                team_name = team_name.split('/')[-1]
                url_name_slug = team_name.replace('.html', '').strip()
                print('LIST', url_name_slug)
                # - call each function
                scraper_dict = get_main_image(scraper_dict, li, url_name_slug)
                scraper_dict = get_flag_img_url(
                    scraper_dict, li, url_name_slug)
                scraper_dict = get_logo_url(scraper_dict, li, url_name_slug)
                scraper_dict = get_podium_finishes(
                    scraper_dict, li, url_name_slug)
                scraper_dict = get_championship_titles(
                    scraper_dict, li, url_name_slug)
                scraper_dict = get_drivers(scraper_dict, li, url_name_slug)
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
                    #     # if they match add to driver object
                    if team.span and team.span.text == detail:
                        team_dict[_slugify(team.span.text)
                                  ] = team.td.text
                        continue
        return team_dict

    except ValueError:
        return "An error occured creating driver data."
