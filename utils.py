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
