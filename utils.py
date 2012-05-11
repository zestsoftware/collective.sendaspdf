import re
import os
import base64

from zExceptions import Unauthorized
from Acquisition import aq_inner, aq_parent, aq_chain

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseFolder
from Products.Five import BrowserView

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

img_sizes = {'image': [],
             'image_listing': [16, 16],
             'image_icon': [32, 32],
             'image_tile': [64, 64],
             'image_thumb': [128, 128],
             'image_mini': [200, 200],
             'image_preview': [400, 400],
             'image_large': [768, 768]}

def get_object_from_url(context, path):
    """ Returns a tuple object, view name, image size, unparsed items.

    View tests/utils.txt for samples.
    """
    obj = context

    for position, element in enumerate(path):
        if element == '..':
            parent = aq_parent(aq_inner(obj))
            if parent is not None:
                obj = parent
            continue

        try:
            obj = getattr(obj, element)
        except AttributeError:
            # Three possibilities here:
            # - the path is broken
            # - the element is a view name
            # - the element defines the image size (in case of images)

            if element in img_sizes:
                return obj, None, element, path[position + 1:]

            try:
                # We sometimes have the problem with Plone 3 where
                # Acquisition seems to not have an effect on getattr
                # or something like that ...
                obj = getattr(aq_parent(obj), element)
                continue
            except AttributeError:
                pass

            # To test the views, we'll use the full aq_chain.
            for ancestor in aq_chain(aq_inner(obj)):
                try:
                    view = ancestor.restrictedTraverse(str(element))
                    if isinstance(view, BrowserView):
                        return ancestor, element, None, path[position + 1:]

                    # Ho, Plone 3 again. An object in the skin folder can not be
                    # accessed via getattr (when in a folder, works when in a document ...).
                    obj = view
                    if position == len(path) - 1:
                        return obj, None, None, None
                    continue

                except (Unauthorized, AttributeError, KeyError, ):
                    pass

            # Ok, we really can't find it now.
            return None, None, None, None

    return obj, None, None, None


def update_relative_url(source, context, embedded_images = True):
    relative_exp = re.compile('((href|src)="([a-zA-Z0-9_=&\-\.\/@\?]+)")', re.MULTILINE|re.I|re.U)
    protocol_exp = re.compile('^(\w+:\/\/).*$')
    image_exp = re.compile('^.*\.(jpg|jpeg|gif|png).*$')
    anchor_exp = re.compile('((href)="(#[^"]+)")', re.MULTILINE|re.I|re.U)
    
    items = relative_exp.findall(source)
    original_url = context.absolute_url()

    mtool = getToolByName(context, 'portal_membership')

    anchor_items = anchor_exp.findall(source)
    for anchor_item in anchor_items:
        attr = anchor_item[1]
        value = anchor_item[2]
        source = source.replace('href="%s"' % value, 'href="%s%s"' % (original_url, value))

    for item in items:
        attr = item[1]
        value = item[2]
                
        if protocol_exp.match(value):
            # That should not happen as ':' should not be recognized
            # by relative_exp.
            continue

        if '?' in value:
            # Just to make things funnier, we have get parameters...
            split = value.split('?')
            value = split[0]
            get_params = '?'.join(split[1:])
        else:
            get_params = None

        path = value.split('/')

        portal_path = getMultiAdapter((context, context.REQUEST), name="plone_portal_state").portal().absolute_url()
        default_replacement = '%s=%s/%s' % (attr, portal_path, value)
        if get_params:
            default_replacement = '%s?%s' % (default_replacement, get_params)

        linked_obj, view, img_size, left_path = get_object_from_url(context, path)

        if linked_obj is None:
            source = source.replace('%s="%s"' % (attr, value), default_replacement)
            continue

        replacement = linked_obj.absolute_url()
        if view:
            replacement += '/%s' % view

        if image_exp.match(value) and attr == 'src' and \
               linked_obj != context and mtool.checkPermission('View', linked_obj):

            if not embedded_images:
                replacement = '%s' % linked_obj.absolute_url()
                if view in ['images', '@@images']:
                    # Image integrated with Plone 4/TinyMCE.
                    replacement += '/@@images/' + '/'.join(left_path)
                elif img_size:
                    replacement += '/' + image_size
            else:
                try:
                    filetype = linked_obj.getImage().getFilename().split('.')[-1]
                    content = linked_obj.getImageAsFile().read()

                    # That's the default image (in it's full size). We'll now try to
                    # resize it.
                    if view in ['images', '@@images'] and left_path and 'image_%s' % left_path[-1] in img_sizes:
                        # Plone 4
                        img_view = linked_obj.restrictedTraverse('@@images')
                        img_w, img_h = img_sizes['image_%s' % left_path[-1]]
                        content = img_view.scale(height = img_h, width = img_w).data

                    elif img_size:
                        content = linked_obj.restrictedTraverse(str(img_size)).data

                except AttributeError:
                    # that's an image in the skin folder.
                    try:
                        filetype = linked_obj.filename.split('.')[-1]
                    except AttributeError:
                        filetype = linked_obj._filepath.split('.')[-1]
                    content = linked_obj._readFile(False)

                replacement = 'data:image/%s;base64,%s' % (
                    filetype,
                    base64.encodestring(content)
                    )

        if get_params:
            replacement += '?%s' % (get_params)

        replacement = '%s="%s"' % (attr, replacement)

        source = source.replace('%s="%s"' % (attr, item[2]),
                                replacement)

    return source
