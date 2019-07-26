from database import db


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
    highest_grid_position = db.Column(db.String(10))

    def __repr__(self):
        return "{0}".format(self.driver_name)

    @classmethod
    def create(self, data):
        db.create_all()
        d = self(
            driver_name=data['driver_name'],
            name_slug=data['driver_slug'],
            date_of_birth=data['date_of_birth'],
            driver_number=data['driver_number'],
            place_of_birth=data['place_of_birth'],
            flag_img_url=data['flag_img_url'],
            main_image=data['main_image'],
            podiums=data['podiums'],
            points=data['points'],
            world_championships=data['world_championships'],
            team=data['team']
        )
        db.session.add(d)
        db.session.commit()
        print(self.query.all())
    # d = driver_model.Driver(
    #     driver_name=data['driver_name'],
    #     name_slug=data['driver_slug'],
    #     date_of_birth=data['date_of_birth'],
    #     driver_number=data['driver_number'],
    #     place_of_birth=data['place_of_birth'],
    #     flag_img_url=data['flag_img_url'],
    #     main_image=data['main_image'],
    #     podiums=data['podiums'],
    #     points=data['points'],
    #     world_championships=data['world_championships'],
    #     team=data['team']
    # )


#  # convert to dict
#         db_data = dict((col, getattr(slug, col))
#                        for col in slug.__table__.columns.keys())
#         # check if any values are changed
#         changed_vals = utils.dict_compare_vals(new_data, db_data)
#         print('XXX', changed_vals)
