from slugify import slugify, Slugify
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'
# compare dict values


def dict_compare_vals(new_data, db_data):
    # loop over new_data
    new_keys_to_add = []
    keys_to_update = []
    for key, val in new_data.items():
        # check for new keys
        if key not in db_data:
            new_keys_to_add.append(key)
        else:
            print('new', val)
            print('old', db_data[key])
            if val != db_data[key]:
                keys_to_update.append(key)
    return {
        'new_keys_to_add': new_keys_to_add,
        'keys_to_update': keys_to_update
    }


def convert_db_row_dict(self, db_dict):
    # https://stackoverflow.com/a/54283540/5972531
    try:
        print("===============================")
        return self.query.filter_by(
            name_slug=db_dict.get('name_slug')).first().__dict__
        return
    except KeyError:
        print("Cannot convert. No key")


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
    # print(fullName)
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
            # print("here", newName)
            return newName
        newName += char


def custom_seperators(word, sep_to_rem, sep_to_add=" "):
    s = word.split(sep_to_rem)
    s = sep_to_add.join(s)
    return s
