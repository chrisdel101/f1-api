from scraper import endpoints
from bs4 import BeautifulSoup
import requests
from user_agent import generate_user_agent

headers = {
    'User-Agent': generate_user_agent(os=None, navigator=None, platform=None, device_type=None),
    'From': 'webdev@chrisdel.ca'
}
