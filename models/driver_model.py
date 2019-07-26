from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(80))
    country = db.Column(db.String(100))
    name_slug = db.Column(db.String(80))
    date_of_birth = db.Column(db.String(20))
    driver_number = db.Column(db.String(10))
    place_of_birth = db.Column(db.String(50))
    flag_img_url = db.Column(db.String(150))
    main_image = db.Column(db.String(150))
    podiums = db.Column(db.String(10))
    points = db.Column(db.String(10))
    world_championships = db.Column(db.String(10))
    team = db.Column(db.String(50))
    highest_grid_position = podiums = db.Column(db.String(10))

    def __repr__(self):
        return "{0}".format(self.name)
