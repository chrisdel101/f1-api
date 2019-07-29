from database import db
from sqlalchemy import text
from slugify import slugify


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(100))
    name_slug = db.Column(db.String(80), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(20))
    driver_number = db.Column(db.String(10))
    place_of_birth = db.Column(db.String(50))
    flag_img_url = db.Column(db.String(150))
    main_image = db.Column(db.String(150))
    podiums = db.Column(db.String(10))
    points = db.Column(db.String(10))
    world_championships = db.Column(db.String(10))
    team = db.Column(db.String(50))
    highest_grid_position = db.Column(db.String(10))
    driver_slug = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "{0}".format(self.driver_name)

    @classmethod
    def new(cls, scraper_dict):
        print('CREATE', scraper_dict)
        db.create_all()
        d = cls()
        d.driver_name = scraper_dict.get('driver_name')
        d.name_slug = slugify(d.driver_name).lower()
        d.country = scraper_dict.get('coutry')
        d.highest_grid_position = scraper_dict.get('highest_grid_position')
        d.driver_name = scraper_dict.get('driver_name')
        d.date_of_birth = scraper_dict.get('date_of_birth')
        d.driver_number = scraper_dict.get('driver_number')
        d.place_of_birth = scraper_dict.get('place_of_birth')
        d.flag_img_url = scraper_dict.get('flag_img_url')
        d.main_image = scraper_dict.get('main_image')
        d.podiums = scraper_dict.get('podiums')
        d.points = scraper_dict.get('points')
        d.world_championships = scraper_dict.get('world_championships')
        d.team = scraper_dict.get('team')
        return d

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            print('INSERT OKAY')
        except Exception as e:
            print('RollBack', e)
            db.session.rollback()

    def delete(self, driver_slug):
        d = self.query.filter_by(name_slug=driver_slug).first()
        try:
            db.session.delete(d)
            db.session.commit()
            print('DELETE OKAY')
        except Exception as e:
            print('Delete Error', e)

    def exists(self, driver_slug):
        try:
            if self.query.filter_by(name_slug=driver_slug).first():
                return True
            return False
        except Exception as e:
            print("Does not exist", e)
            return False
