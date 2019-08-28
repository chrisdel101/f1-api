import datetime
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


def teamShortener(fullName):
    if fullName == 'Haas F1 Team':
        return 'Haas'
    # count whitespaces - get num of words
    whiteSpaces = len(fullName.split(' ')) - 1
    # 2 words or toro rosso, etc
    if whiteSpaces <= 1:
        return fullName
    #  else more than 2 words - red bull racing etc
    splitName = list(fullName)
    newName = ''
    whiteSpace = 0
    for char in splitName:
        if char == ' ':
            whiteSpace += 1
        if whiteSpace >= whiteSpaces:
            return newName
        newName += char


def custom_seperators(word, sep_to_rem, sep_to_add=" "):
    s = word.split(sep_to_rem)
    s = sep_to_add.join(s)
    return s


# takes dict like {'name_slug': 'red_bull_racing', 'name': 'Red Bull Racing'}
# returns a string
def create_url_name_slug(team_name_dict):
    if type(team_name_dict) is not dict:
        raise TypeError('utils.create_url_name_slug must take a dict.')
    try:
        full_name = utils.custom_seperators(team_name_dict['name'], "_")
        # shorten to match urls
        shortened_name = utils.teamShortener(full_name)
        # remove underscores - add dashes to match urls
        shortened_url_name = utils.custom_seperators(shortened_name, '_', '-')
        # remove whitespace - add dashes
        url_name_slug = utils.custom_seperators(shortened_url_name, ' ', '-')
        return url_name_slug
    except Exception as e:
        print('an error in utils.create_url_name_slug', e)


# takes string of name
# returns {'name_slug': 'lewis-hamilton', 'name': 'Lewis Hamilton'}
def create_driver_list(driver_list):
    try:
        new_list = []
        for driver in driver_list:
            d = {
                'driver_name': driver,
                'name_slug': slugify(driver).lower()
            }
            new_list.append(d)
        return new_list
    except Exception as e:
        print('an errot in utils.create_driver_list', e)


# takes an instance and a model name - if new instance has None - record the props
def compare_current_to_stored(current_sql_instance, class_to_check):
    # use slug from new class to query for stored
    slug = current_sql_instance.name_slug
    # look up same class in DB
    query_stored = class_to_check.query.filter_by(name_slug=slug).first()
    # if nothing stored yet return true
    if query_stored == None:
        return True
    # loop over stored instance
    changed_vals = {}
    for key, value in vars(query_stored).items():
        # pass
        if key != "_sa_instance_state" and key != 'id':
            # don't compate _sa_instance or id
            if vars(current_sql_instance)[key] != value:
                # compare storesd to new class
                if vars(current_sql_instance)[key] == None:
                    changed_vals[key] = vars(current_sql_instance)[key]
                    print(f"new instance #{key} is none")
    # print(changed_vals)
    # if empty dict, no changes
    if not changed_vals:
        return True
        # else return all changes
    else:
        print('HERE')
        return changed_vals


def log_None_values(dict_to_log):
    try:
        # make sure
        if None not in dict_to_log.values():
            return 'No None values to log'
        # add timestamp
        dict_to_log['timestamp'] = datetime.datetime.now().strftime(
            "%d/%m/%y %H:%M")
        # add to txt file
        with open('none_log.txt', 'a', encoding='utf-8') as f:
            json.dump(dict_to_log, f, ensure_ascii=False, indent=4)
    except Exception as e:
        return('An error ocurred in utils.log_None_vals:', e)
