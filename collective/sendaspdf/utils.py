import re
import os

from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS

try:
    # Python 2.6 (maybe 2.5 too)
    import hashlib

    def md5_hash(string, salt = ''):
        return hashlib.md5(salt + string).hexdigest()
except:
    # Python 2.4
    import md5

    def md5_hash(string, salt = ''):
        return md5.md5(salt + string).hexdigest()

def decode_parameter(p):
    """ Decode a parameter/value from a URL format to
    a more readable version.
    Based on table seen in this page.
    http://www.blooberry.com/indexdot/html/topics/urlencoding.htm

    >>> from collective.sendaspdf.utils import decode_parameter
    >>> decode_parameter('kikoo%20lol')
    'kikoo lol'

    Well, if there is nothing to do, we do nothing.
    >>> decode_parameter('kikoolol')
    'kikoolol'

    It might mainly be used to decode the 'came_from' parameter.
    >>> decode_parameter('http%3A//www.prettigpersoneel.nl/nerull-ii/%3Fview%3Demployees')
    'http://www.prettigpersoneel.nl/nerull-ii/?view=employees'

    We decode the '%' caracter last so we can not have confusion.
    >>> decode_parameter('%252C')
    '%2C'
    
    If we did not decode it last, we could have obtained ','.
    """
    table = {'24': '$',
             '26': '&',
             '2C': ',',
             '2F': '/',
             '3A': ':',
             '3B': ';',
             '3D': '=',
             '3F': '?',
             '40': '@',
             '20': ' ',
             '22': '"',
             '3C': '<',
             '3E': '>',
             '23': '#',
             '7B': '{',
             '7D': '}',
             '7C': '|',
             '5C': '\\',
             '5E': '^',
             '7E': '~',
             '5B': '[',
             '5D': ']',
             '60': '`'}

    for k in table:
        if k == '25':
            continue
        p = p.replace('%' + k, table[k])
    return p.replace('%25', '%')

def extract_from_url(url, context_url):
    """ Extracts the view name and the list of get
    parameters from an URL, using the base context URL
    to extract the view name.

    >>> from collective.sendaspdf.utils import extract_from_url

    If the URL does not start with the context_url, wwe can
    not do anything.
    >>> extract_from_url('http://bla.com', 'https://bla.com')
    (None, None)

    If the two addresses are the same, we do not have any
    get parameter or view.
    >>> context_url = 'http://bla.com/my_folder/my_context'
    >>> extract_from_url(context_url, context_url)
    ('', {})

    We can recognize the views with or without '@@' in front.
    >>> extract_from_url(context_url + '/my_view', context_url)
    ('my_view', {})

    >>> extract_from_url(context_url + '/@@my_view', context_url)
    ('my_view', {})

    It can also extract the list of GET parameters.
    >>> extract_from_url(context_url + '?p1=12', context_url)
    ('', {'p1': '12'})

    Even for multiple parameters of course.
    >>> extract_from_url(context_url + '?p1=12&p2=blabla', context_url)
    ('', {'p2': 'blabla', 'p1': '12'})

    If a GET parameter if present twice, then he corresponding value
    in the dictionnary will be a list containing all values.
    >>> extract_from_url(context_url + '?p1=12&p2=blabla&p2=blublu', context_url)
    ('', {'p2': ['blabla', 'blublu'], 'p1': '12'})

    The system can recognise parameters with special caracters.
    >>> extract_from_url(
    ...     'http://127.0.0.1:8080/hostedhrm/acl_users/credentials_cookie_auth/require_login?came_from=http%3A//127.0.0.1%3A8080/hostedhrm/nerull-ii/nerull-ii/test-floating-contract%3Fwidget_id%3DplonehrmAbsenceWidget%26mode%3Dpercentage%26UID%3Dea267a725dc3ea79b4e67902d221e04e',
    ...     'http://127.0.0.1:8080/hostedhrm/acl_users/credentials_cookie_auth/')
    ('require_login',
     {'came_from': 'http://127.0.0.1:8080/hostedhrm/nerull-ii/nerull-ii/test-floating-contract?widget_id=plonehrmAbsenceWidget&mode=percentage&UID=ea267a725dc3ea79b4e67902d221e04e'})    

    """
    if not url.startswith(context_url):
        return None, None

    carac_class = '[A-Za-z0-9_ %/\\.\\-]'

    reg = r'^' + context_url + '/? ' + \
            '?((@@)?(' + carac_class + '*)/?)?' + \
            '(\\?((' + carac_class + '+=' + carac_class+ '*&?)*))?' + \
            '(#.*)?$'
    match = re.split(reg, url)
    if len(match) == 1:
        return None, None

    view_name = match[3]

    # We still need to extract parameters more propertly.
    get_params = {}
    if match[6]:
        for couple in match[5].split('&'):
            try:
                key, value = couple.split('=')
                key = decode_parameter(key)
                value = decode_parameter(value)

                if key in get_params:
                    if not type(get_params[key]) == list:
                        get_params[key] = [get_params[key]]
                    get_params[key].append(value)
                else:
                    get_params[key] = value
            except:
                pass
    return view_name, get_params

def find_filename(path, filename, extension='pdf'):
    """ Finds a non-conflicting filename in the
    directory given by path.

    >>> import os
    >>> from collective.sendaspdf.utils import find_filename

    If the path is not correct, returns nothing.
    If this test fails, I'm not responsible for the fact that you
    have a 'kikoolol' directory in the root of your system ;)
    >>> find_filename('/kikoolol', '')

    Some faking for the tests.
    >>> def fake_listdir(path):
    ...     return ['file.pdf', 'file1.pdf', 'file2.pdf', 'file3.pdf',
    ...             'file.html', 'file1.html', 'file2.html']

    >>> os.old_listdir = os.listdir
    >>> os.listdir = fake_listdir

    A example without conflict.
    >>> find_filename('', 'my_file')
    'my_file.pdf'

    No conflict and a custom extension.
    >>> find_filename('', 'my_file', 'html')
    'my_file.html'

    If there is a conflict, the function adds a number
    at the end.
    >>> find_filename('', 'file')
    'file4.pdf'

    >>> find_filename('', 'file', 'html')
    'file3.html'

    """
    try:
        files = os.listdir(path)
    except:
        # This shall not happen, except if the path has not
        # been set correctly.
        return

    # We check the file name is not already used in the directory.
    # If so, we try to prepend a number at the end.
    if filename + '.' + extension in files:
        postfix = 1
        while postfix <= RENAME_AFTER_CREATION_ATTEMPTS:
            if '%s%s.%s' % (filename, postfix, extension) in files:
                postfix += 1
                continue

            filename = '%s%s' % (filename, postfix)
            break

        if postfix > RENAME_AFTER_CREATION_ATTEMPTS:
            return

    return filename + '.' + extension
