import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/f1'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config.update(
#     SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI'],
#     SQLALCHEMY_TRACK_MODIFICATIONS=app.config['SQLALCHEMY_TRACK_MODIFICATIONS'],
# )
