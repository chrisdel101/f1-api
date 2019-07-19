

def extract_name_whitespace(str):
    text_aft_whitespace = False
    text_touched = False
    space_added = False
    new_str = ""
    for i in str:
        # firsr letter run
        if i != " " and not text_touched and not text_aft_whitespace:
            new_str += i
            text_touched = True
        # all letters first word
        elif i != " " and text_touched and not text_aft_whitespace:
            new_str += i
        # set on first space after text
        elif i == " " and text_touched:
            text_aft_whitespace = True
        # next letter after space - add a space in word here
        elif i != " " and text_aft_whitespace and not space_added:
            new_str += " "
            new_str += i
            space_added = True
        # rest of second word
        elif i != " " and text_aft_whitespace and space_added:
            new_str += i
    print('new', new_str)
    return new_str
