from sqlalchemy.orm import validates
import os
from database import db
from sqlalchemy import text
import models
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, unique=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
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
    # passed in data must be a dict in all cases
    def new(cls, sender_id, data={}):
        print('data new', data)
        try:
            # if no id send to exception - to pass test
            if sender_id == None:
                raise ValueError('id cannot be None')
            elif data['username'] == None:
                raise ValueError('username cannot be none')
            elif data['password'] == None:
                raise ValueError('password cannot be none')
            db.create_all()
            d = cls()
            d.id = sender_id
            d.username = data.get('username')
            d.password = data.get('password')
            return d
        except Exception as e:
            print('Error in User new:', e)
            return e

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            # not working propely
            print("Error in encode_auth_token", e)

    def insert(self):
        try:
            if not self.id:
                raise AssertionError('insert Error: ID cannot be None')
            db.session.add(self)
            db.session.commit()
            print('INSERT OKAY')
        except Exception as e:
            print('Insert error', e)

    # data is a dict
    def update(self, data):
        try:
            # assign new data to self obj
            if data.get('driver_data'):
                self.driver_data = data['driver_data']
            if data.get('team_data'):
                self.team_data = data['team_data']
            # save to DB
            db.session.commit()
            print('UPDATE OKAY')
        except Exception as e:
            print('Update error', e)

    def delete(self, sender_id):
        d = self.query.filter_by(id=sender_id).first()
        try:
            db.session.delete(d)
            db.session.commit()
            print('DELETE OKAY')
        except Exception as e:
            print('Delete Error', e)

    # sender_id is same as id, but id is seems like resvered var
    def exists(self, sender_id):
        try:
            if self.query.filter_by(id=sender_id).first():
                return True
            return False
        except Exception as e:
            print("Error in exists", e)
            return False

    def as_dict(req):
        return {c.name: getattr(req, c.name) for c in req.__table__.columns}
