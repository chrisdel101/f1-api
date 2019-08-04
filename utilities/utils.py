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
