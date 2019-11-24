import os
from database import db
from sqlalchemy import text
import models
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_data = db.Column(db.PickleType)
    team_data = db.Column(db.PickleType)

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v)
                           for k, v in self.__dict__.items()),
        )

    @classmethod
    def new(cls, id, data):
        print('here')
        try:
            db.create_all()
            d = cls()
            d.id = id
            d.driver_data = data.get('driver_data')
            # short version with spaces
            d.team_data = data.get('team_data')
            print('d', d)
            return d
        except Exception as e:
            print('Error in User new:', e)
