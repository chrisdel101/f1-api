from models import driver_model
from utilities import scraper
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def scrape():
    # -get all driver names
    all_drivers = scraper.scrape_all_driver_names()
    # - loop over names and scrape each
    for driver in all_drivers:
        driver_slug = slugify(driver).lower()
    # - insert on scrape into DB
        new_data = scraper.scrape_single_driver_stats(driver_slug)
        d = driver_model.Driver.new(new_data)
        if d.exists(driver_slug):
            d.delete(driver_slug)
        d.insert()

    return d
