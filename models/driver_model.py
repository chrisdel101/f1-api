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
    driver_slug = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "{0}".format(self.driver_name)

    @classmethod
    def create(cls, data_dict):
        print('CREATE')
        db.create_all()
        d = cls()
        d.driver_name = data_dict.get('driver_name')
        d.name_slug = data_dict.get('name_slug')
        d.country = data_dict.get('coutry')
        d.highest_grid_position = data_dict.get('highest_grid_position')
        d.driver_name = data_dict.get('driver_name')
        d.name_slug = data_dict.get('driver_slug')
        d.date_of_birth = data_dict.get('date_of_birth')
        d.driver_number = data_dict.get('driver_number')
        d.place_of_birth = data_dict.get('place_of_birth')
        d.flag_img_url = data_dict.get('flag_img_url')
        d.main_image = data_dict.get('main_image')
        d.podiums = data_dict.get('podiums')
        d.points = data_dict.get('points')
        d.world_championships = data_dict.get('world_championships')
        d.team = data_dict.get('team')
        try:
            db.session.add(d)
            db.session.commit()
        except:
            print('RollBack')
            db.session.rollback()
        return d

    def compare(self, data_dict):
        db_dict = utils.convert_db_row_dict(self, data_dict)
        result = utils.dict_compare_vals(data_dict, db_dict)
        return {
            compare_results: results,
            db_dict: db_dict
        }

    def update(self, data_dict):

        results = compare(self, data_dict)
        print(self)
        try:
            if len(results.compare_results['new_keys_to_add']):
                print('Migration needed - cols to add')
            else:
                # -query for driver slug and deltete
                print(results.db_dict)
        except:
            print('ModelError')

    def exists(self, driver_slug):
        try:
            if self.query.filter_by(name_slug=driver_slug).first():
                return True
            return False
        except:
            print("Does not exist")
            return False
