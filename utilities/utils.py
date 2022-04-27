import bcrypt
import os
import datetime
from datetime import timedelta
from flask import jsonify
import json
from utilities import utils
import re
from slugify import slugify, Slugify
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def serialize(l, lowerCase=True):
    dict = {}
    try:
        for item in l:
            item_slug = slugify(str(item))
            if lowerCase:
                item_slug = item_slug.lower()
            if item_slug not in dict:
                dict[item_slug] = str(item)
        return dict
    except Exception as e:
        print("serialize error", e)


def serialize_row(row):
    # https://stackoverflow.com/a/10370224/597253
    try:
        if type(row) is not dict:
            row = dict(row)
        # remove the field causing the error
        row.pop('_sa_instance_state', None)
        return row
    except Exception as e:
        print("Serialize Error", e)


# used in create_team_header_from_slug
# headerize, Alfa Romeo Racing to Alfa
def headerize_team_tame(name):
    if name == 'Haas F1 Team':
        return 'Haas'
    # count whitespaces - get num of words
    whiteSpaces = len(name.split(' ')) - 1
    # 2 words or toro rosso, etc
    if whiteSpaces <= 1:
        return name
    #  else more than 2 words - red bull racing etc
    splitName = list(name)
    newName = ''
    whiteSpace = 0
    for char in splitName:
        if char == ' ':
            whiteSpace += 1
        if whiteSpace >= whiteSpaces:
            return newName
        newName += char


# remove/add separators from a string
def word_seperator_manager(word, sep_to_rem, sep_to_add=" "):
    s = word.split(sep_to_rem)
    s = sep_to_add.join(s)
    return s


# takes team_slug and returns header name Red-Bull
def create_team_header_from_slug(team_name_slug):
    try:
        # print('team_name_slug', team_name_slug)
        if team_name_slug == 'mclaren':
            return 'McLaren'
        if team_name_slug == 'alphatauri':
            print('HERE', team_name_slug)
            return 'AlphaTauri'
        # strip underscores
        stripped_slug = utils.word_seperator_manager(team_name_slug, '_')
        # capitalize each word
        cap_each_word_list = [f'{word[0].upper()}{word[1:len(word)]}'
                              for word in stripped_slug.split(' ')]
        # headerize, Alfa Romeo Racing to Alfa Romeo
        headerized_team_name = utils.headerize_team_tame(
            ' '.join(cap_each_word_list))
        # hypenate headerized_team_name
        #  Alfa Romeo to  Alfa-Romeo
        team_name_header = utils.word_seperator_manager(
            headerized_team_name, ' ', '-')
        return team_name_header
    except Exception as e:
        print('an error in utils.create_team_header_from_slug', e)


# takes team_name and returns header name Red-Bull
def create_team_header_from_team_name(team_name):
    try:
        # print('team_name', team_name)
        if team_name == 'mclaren':
            return 'McLaren'
        if team_name == 'alphatauri':
            print('HERE', team_name)
            return 'AlphaTauri'
        # strip underscores
        stripped_slug = utils.word_seperator_manager(team_name, '_')
        # capitalize each word
        cap_each_word_list = [f'{word[0].upper()}{word[1:len(word)]}'
                              for word in stripped_slug.split(' ')]
        # headerize, Alfa Romeo Racing to Alfa Romeo
        headerized_team_name = utils.headerize_team_tame(
            ' '.join(cap_each_word_list))
        # hypenate headerized_team_name
        #  Alfa Romeo to  Alfa-Romeo
        team_name_header = utils.word_seperator_manager(
            headerized_team_name, ' ', '-')
        return team_name_header
    except Exception as e:
        print('an error in utils.create_team_header_from_slug', e)


# takes string of name
# returns {'name_slug': 'lewis-hamilton', 'name': 'Lewis Hamilton'}
def create_driver_list(driver_list):
    try:
        new_list = []
        for driver in driver_list:
            d = {
                'driver_name': driver.strip(),
                'name_slug': slugify(driver).lower().strip()
            }
            new_list.append(d)
        return new_list
    except Exception as e:
        print('an errot in utils.create_driver_list', e)


# hash password before storing
def hash_password(password):
    # password = bytes(password, encoding='utf-8')
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# return T if matches else F
def check_hashed_password(password, hashed):
    try:
        # re-encode PW before checking
        password = bytes(password, encoding='utf-8')
        return bcrypt.checkpw(password, hashed)
    except Exception as e:
        print('error in check_hashed_password', e)


# set time for sessions to last
def set_session_time(session, app, mins):
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=mins)


# TODO
# - slug checker
# - header checker
# - team_name checker
