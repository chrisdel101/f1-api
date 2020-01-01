import os
from database import db
import models
from utilities import utils
from flask_login import UserMixin
import jwt
import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.BigInteger, primary_key=True, unique=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(), nullable=False)
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
        try:
            # if no id send to exception - to pass test
            if not sender_id:
                raise ValueError('id cannot be None')
            elif not data.get('username'):
                raise ValueError('username cannot be none')
            elif not data.get('password'):
                raise ValueError('password cannot be none')
            db.create_all()
            d = cls()
            d.id = sender_id
            d.username = data.get('username')
            # hash password
            password = utils.hash_password(data.get('password'))
            print('PASSWORD', password)
            d.password = password
            if os.environ['LOGS'] != 'off':
                print('new user', d)
            return d
        except Exception as e:
            print('user new error', e)
            raise e

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                os.environ['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            # not working propely
            print("Error in encode_auth_token", e)
            raise e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(
                auth_token, os.environ['SECRET_KEY'], algorithms='HS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            print('Signature expired. Please log in again.')
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            print('Invalid token. Please log in again.')
            return 'Invalid token. Please log in again.'

    def insert(self):
        try:
            if not self.id:
                raise AssertionError('insert Error: ID cannot be None')
            db.session.add(self)
            db.session.commit()
            print('INSERT OKAY')
        except Exception as e:
            print('Rollback:', e)
            raise e

    # data is a dict
    def update(self, data):
        try:
            # assign new data to self obj
            if data.get('driver_data'):
                self.driver_data = data['driver_data']
            if data.get('team_data'):
                self.team_data = data['team_data']
            if data.get('password'):
                self.password = self.hash_password(data['password'])
            # save to DB
            db.session.commit()
            print('UPDATE OKAY')
        except Exception as e:
            print('user update error', e)
            raise e

    def delete(self, sender_id):
        d = self.query.filter_by(id=sender_id).first()
        try:
            db.session.delete(d)
            db.session.commit()
            print('DELETE OKAY')
        except Exception as e:
            print('user delete error', e)
            raise e

    # sender_id is same as id, but id is seems like resvered var
    def exists(self, lookup, lookup_type='id'):
        try:
            # with username
            if lookup_type == 'username':
                if self.query.filter_by(username=lookup).first():
                    return True
            # default - with id
            else:
                if self.query.filter_by(id=lookup).first():
                    return True
            return False
        except Exception as e:
            print("error in exists", e)

    def as_dict(req):
        return {c.name: getattr(req, c.name) for c in req.__table__.columns}
