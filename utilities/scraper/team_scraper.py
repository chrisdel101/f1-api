from bs4 import BeautifulSoup, UnicodeDammit
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


# takes dict of teams adds main image to each team
# outputs altered dict
def get_main_image(scraper_dict):
    if type(scraper_dict) is not dict:
        raise TypeError('get_main_image must take a dict.')
    try:
        soup = _team_page_scrape()
        all_teams = soup.find('ul', {'class', 'teamindex-teamteasers'})
        url_name_slug = None
        main_img = None
        # loop over all teams on the page
        for li in all_teams.find_all('li'):
            # get name on each team a-href
            if li.find('a'):
                # strip all text to get matching url_name_slug
                team_name = li.find('a')['href']
                team_name = team_name.split('/')[-1]
                url_name_slug = team_name.replace('.html', '').strip()
                # find main team img
                if li.find('div', {'class', 'teamteaser-image'}) and li.find('div', {'class', 'teamteaser-image'}).find('img'):
                    # print('\n')
                    main_img_src = li.find(
                        'div', {'class', 'teamteaser-image'}).find('img')['src']
                    # resize img
                    main_img_src = _change_team_img_size(main_img_src, 3)
                    main_img = "{0}/{1}".format(
                        endpoints.home_endpoint(), main_img_src)
                    # print(url_name_slug)
                    # attach main_img to current team
                    if scraper_dict['url_name_slug'] == url_name_slug:
                        scraper_dict['main_image'] = main_img
        # print(scraper_dict)
        return scraper_dict
    except Exception as e:
        print('error in team main_image', e)


def _team_images():
    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    team_info = soup.find('div', {'class', 'teamteaser-details'})
    # print(team_info('span', {'class','teamteaser-flag'}))
    team_dict = {}
    try:
        # flag img
        if team_info('span', {'class', 'teamteaser-flag'}) and team_info('span', {'class', 'teamteaser-flag'})[0].img:
            flag_img_url = team_info(
                'span', {'class', 'teamteaser-flag'})[0].img['src']
            team_dict['flag_img_url'] = '{0}{1}'.format(
                endpoints.home_endpoint(), flag_img_url)
        else:
            print('Warning: No flag-img for team found.')
        # team title
        if team_info('h2', {'class', 'teamteaser-title'}):
            title = team_info('h2', {'class', 'teamteaser-title'})[0].text
            team_dict['title'] = title.strip()
        else:
            print("Warning: No title for team found.")
        # driver names
        if team_info('ul'):
            drivers = []
            for driver in team_info.find_all('li'):
                drivers.append(driver.text)
            team_dict['drivers'] = drivers
        else:
            print("Warning: No drivers for team found.")

        if team_info('div', {'class', 'teamteaser-sponsor'}) and team_info('div', {'class', 'teamteaser-sponsor'})[0].img:
            team_logo_src = team_info(
                'div', {'class', 'teamteaser-sponsor'})[0].img['src']
            team_logo = '{0}{1}'.format(
                endpoints.home_endpoint(), team_logo_src)
            team_dict['logo'] = team_logo
        else:
            print('Warning: No logo for team found.')
        # main
        if soup.find('div', {'class', 'teamteaser-image'}) and soup.find('div', {'class', 'teamteaser-image'}).img:
            img_src = soup.find(
                'div', {'class', 'teamteaser-image'}).img['src']
            new_str = _change_team_img_size(img_src, 3)
            team_dict['main_image'] = "{0}/{1}".format(
                endpoints.home_endpoint(), new_str)
        else:
            print('Warning: No main-image for team found.')

        # print('DICT', team_dict)
        return team_dict
    except ValueError:
        return "An error occured creating driver images."


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
