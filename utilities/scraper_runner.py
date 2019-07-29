from models import driver_model
from utilities import scraper
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def scrape():
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
        if d.exists(driver_slug):
            d.delete(driver_slug)
        d.insert()

    return d
