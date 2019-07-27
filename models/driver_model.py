from database import db
import utils
from sqlalchemy import text


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

    def __repr__(self):
        return "{0}".format(self.driver_name)

    @classmethod
    def create(self, data_dict):
        print('CREATE')
        db.create_all()
        d = self(
            driver_name=data_dict.get('driver_name'),
            name_slug=data_dict.get('driver_slug'),
            date_of_birth=data_dict.get('date_of_birth'),
            driver_number=data_dict.get('driver_number'),
            place_of_birth=data_dict.get('place_of_birth'),
            flag_img_url=data_dict.get('flag_img_url'),
            main_image=data_dict.get('main_image'),
            podiums=data_dict.get('podiums'),
            points=data_dict.get('points'),
            world_championships=data_dict.get('world_championships'),
            team=data_dict.get('team')
        )

        db.session.add(d)
        db.session.commit()

    @classmethod
    def update(self, data_dict):
        db_dict = utils.convert_db_row_dict(self, data_dict)
        result = utils.dict_compare_vals(data_dict, db_dict)
        try:
            sql = text('SELECT * FROM driver')
            result = db.session.execute(text('SELECT * FROM driver'))
            print('RES', result)
            for r in result:
                print('what', [0])  # Access by positional index
                # Access by column name as a string
                print('name', r['driver_name'])
                # convert to dict keyed by column names
                r_dict = dict(r.items())
        except:
            print('Error')

    @classmethod
    def exists(self, driver_slug):
        if self.query.filter_by(name_slug=driver_slug).first():
            return True
        return False
