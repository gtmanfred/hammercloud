import os
import re
import six


def valid_uuid(uuid):
    '''
    validate that the 'uuid' is a uuid4
    '''
    regex = re.compile((
        r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-'
        r'?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z'
    ), re.I)
    match = regex.match(six.text_type(uuid))

    if match:
        return uuid
    return False


def gettermsize():
    '''
    horrible non-portable hack to get the terminal size to transmit
    to the child process spawned by pexpect
    '''
    # works on Mac OS X, YMMV
    (rows, cols) = os.popen("stty size").read().split()
    rows = int(rows)
    cols = int(cols)
    return (rows, cols)


def get_entry(dict_, key, value):
    '''
    get object with key == value inside it
    '''
    for entry in dict_:
        if entry[key] == value:
            return entry
    return {}
