import endpoints
from bs4 import BeautifulSoup
import requests
from user_agent import generate_user_agent
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify.separator = '_'

headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}


def list_all_teams():
    page = requests.get(endpoints.teams_endpoint(), headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    ul_teams_list = soup.find('ul', {'class', 'teamindex-teamteasers'})
    teams = []
    li_team_list = ul_teams_list.find_all('li')
    for team in li_team_list:
        if team.find('h2'):
            print(_slugify(team.find('h2').text))
            name = "".join(_slugify(team.find('h2').text).split())
            teams.append(name)

    return teams
