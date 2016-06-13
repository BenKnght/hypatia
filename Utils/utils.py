def upsert(dictionary, key, value):
    """
    insert or update a key in a dictionary having a list as value
    {'a': [1, 3], 'b', [4, 5]}
    :param dictionary: dictionary to insert or update
    :param key: key to check if exists and append if exists, else create with singleton list of value
    :param value: value to insert or append
    :return: None
    """
    if key in dictionary:
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]


def upsert_dict(dictionary, key, sub_key, value):
    """
    insert or update a key in a dictionary having an inner dictionary as value
    {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
    :param dictionary: dictionary to insert or update based on presence of key
    :param key: key which decides insert or update, 'a' and 'd' above are keys
    :param sub_key: key for inner dictionary
    :param value: value for the sub_key
    :return: None
    """
    if key in dictionary:
        dictionary[key][sub_key] = value
    else:
        dictionary[key] = {sub_key: value}


def upsert_dict_arr(dictionary, key, sub_key, value):
    """
    insert or update a key in a dictionary having an inner dictionary as value
    However the value is a list here
    {'a': {'b': [1, 2], 'c': [2]}, 'd': {'e': [3, 4], 'f': [4, 5, 6]}}
    :param dictionary: dictionary to insert or update based on presence of key
    :param key: key which decides insert or update, 'a' and 'd' above are keys
    :param sub_key: key for inner dictionary
    :param value: value for the sub_key
    :return: None
    """
    if key in dictionary:
        if sub_key in dictionary[key]:
            dictionary[key][sub_key].append(value)
        else:
            dictionary[key][sub_key] = [value]
    else:
        dictionary[key] = {sub_key: [value]}


def median(arr):
    """
    Computes the median for a list of numbers
    :param arr: list of integers
    :return: median
    """
    arr.sort()
    length = len(arr)
    if length % 2 == 0:
        return (arr[length / 2] + arr[(length / 2) - 1]) / 2
    return arr[length / 2]


def mean(arr):
    """
    Computes the mean of an array of numbers
    :param arr: list of numbers
    :return: mean
    """
    return sum(arr) / len(arr)
