def remove_extra_spaces_from_string(string):
    if string[0] == ' ':
        return remove_extra_spaces_from_string(string[1:])
    elif string[len(string) - 1] == ' ':
        return remove_extra_spaces_from_string(string[:len(string) - 1])
    else:
        return string


# returns a median in a list of floats. If the list is empty - median is 99999
def helper_median(some_list):
    if len(some_list) == 0:
        return 99999
    return some_list[int(len(some_list)/2)]


# returns a mean for a list If the list is empty - median is 99999
def helper_mean(some_list):
    total = 0.0
    if len(some_list) == 0:
        return 99999
    for item in some_list:
        total += item
    return float(total/len(some_list))


# generates a line of this template: fullname == \"xxx" or fullname ....
def generate_good_or_line(names_list):
    first_item = True
    temp_line = ""
    for item in names_list:
        if first_item:
            temp_line += 'item.FullName == \\"' + item + '\\"'
            first_item = False
        else:
            temp_line += ' or item.FullName == \\"' + item + '\\"'
    return temp_line
