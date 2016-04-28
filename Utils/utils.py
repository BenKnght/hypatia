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
