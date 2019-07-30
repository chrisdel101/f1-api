from models import driver_model, team_model
from slugify import slugify, Slugify
from utilities import scraper, utils
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def main():
    # scrape_drivers()
    scrape_teams()


# - scrapes all drivers & inserts into DB
# returns unused dict
def scrape_drivers():
    # -get all driver names
    all_drivers = scraper.scrape_all_driver_names()
    # - loop over names
    for driver in all_drivers:
        # slugify name
        driver_slug = slugify(driver).lower()
        # scrape each driver
        new_data = scraper.scrape_single_driver_stats(driver_slug)
    # - insert on scrape into DB
        d = driver_model.Driver.new(new_data)
        print('DD', d)
        if d.exists(driver_slug):
            d.delete(driver_slug)
        d.insert()

    return d


def scrape_teams():
    # -get all driver names
    all_teams = scraper.scrape_all_team_names()
    print('ALL', all_teams)
    # - loop over names
    for team in all_teams:
        #     # remove all separators for count
        name = utils.custom_seperators(team['name'], "_")
    #     # shorten to match urls
        name = utils.teamShortener(name)
    #     # print(name)
    #     # print(name)
    #     # remove underscores - add dashes to match urls
        name = utils.custom_seperators(name, '_', '-')
    #     # # remove whitespace - add dashes
        name = utils.custom_seperators(name, ' ', '-')
    #     print(name)

    # # scrape each team
        new_data = scraper.scrape_single_team_stats(name)
    # print(new_data)
    # - insert on scrape into DB
        d = team_model.Team.new(new_data)
        print('d', d)
    # # return
        if d.exists(team['name_slug']):
            d.delete(team['name_slug'])
        d.insert()

    return d


# if__name__ == "__main__"
# main()
