from bs4 import BeautifulSoup, UnicodeDammit
import requests
import re
from user_agent import generate_user_agent
from slugify import slugify, Slugify
import sys
sys.path.insert(
    1, '/Users/chrisdielschnieder/desktop/code_work/formula1/f1Scraper/f1scraper-flask/utilities')
# from utilities import endpoints
import endpoints
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


# -  caps team name
# - return dict
def _team_images(name):

    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    print('soup')
    team_info = soup.find('div', { 'class', 'teamteaser-details'})
    # print(team_info('span', {'class','teamteaser-flag'}))
    team_dict = {}
    try:
        if team_info('span', {'class','teamteaser-flag'}) and  team_info('span', {'class','teamteaser-flag'})[0].img:
            flag_img_url = team_info('span', {'class','teamteaser-flag'})[0].img['src']
            team_dict['flag_img_url'] = '{0}{1}'.format(endpoints.home_endpoint(),flag_img_url)

        if team_info('h2', {'class', 'teamteaser-title'}):
            title = team_info('h2', {'class', 'teamteaser-title'})[0].text
            team_dict['title'] = title.strip()
        else:
            print("Error: No name for driver found.")

        if team_info('ul'):
            drivers = []
            for driver in team_info.find_all('li'):
                drivers.append(driver.text)
            team_dict['drivers'] = drivers
        else:
            print("Error: No flag-icon for driver found.")
        print('DICT', team_dict)
        return team_dict
    except ValueError:
        return "An error occured creating driver images."


_team_images('Mercedes')


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
