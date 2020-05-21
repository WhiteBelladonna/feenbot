def lookup(values, key):

    for item in values:

        if item[0] == key:

            return item[1]

    return