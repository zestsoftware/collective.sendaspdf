import os
from datetime import datetime

from AccessControl import Unauthorized
from Products.validation import validation
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string

from collective.sendaspdf import transforms
from collective.sendaspdf.utils import md5_hash
from collective.sendaspdf.utils import extract_from_url
from collective.sendaspdf.utils import find_filename
from collective.sendaspdf.emailer import send_message

class BaseView(BrowserView):
    """ Class used to factorize some code for the different views
    used in the product.
    """
    error_mapping = {'email': ['email', 'invalid_email'],
                     'email_recipient': ['email_recipient',
                                         'invalid_email_recipient']}

    def __init__(self, *args, **kwargs):
        """ We just need to define some instance variables.
        """
        super(BaseView, self).__init__(*args, **kwargs)

        # The list of errors found when checking the form.
        self.errors = []

        # XXX - this should be changed in the future,
        # using site properties so the users can manage this
        # from the ZMI.
        self.tempdir = '/tmp/' #XXX - use tempdir
        self.salt = 'kikoo'
        self.filename_in_mail = 'screenshot.pdf'
        # We can use here any module name from collective.sendaspdf.transforms
        # (ok, for we just have the choice between 'pisa' and 'wk')
        self.pdf_generator = 'wk'

        self.pdf_file = None
        self.filename = ''

    def get_user(self):
        """ Returns the currently logged-in user.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            return

        return mtool.getAuthenticatedMember()

    def get_user_fullname(self):
        """ Returns the currently logged-in user's fullname.
        """
        member = self.get_user()
        if member:
            return member.getProperty('fullname')

    def get_user_email(self):
        """ Returns the currently logged-in user's email.
        """
        member = self.get_user()
        if member:
            return member.getProperty('email')

    def generate_filename_prefix(self):
        """ Returns the user's email hashed in md5 followed
        by an underscore.
        If we can not get an email (the user is anonymous or
        email is not mandatory in the system), returns an empty
        string.

        We extract it from 'generate_temp_filename as we will
        also use this sytem to be sure that the user has
        access to the file when sending it.
        """
        email = self.get_user_email()
        if not email:
            return ''

        return '%s_' % md5_hash(email, self.salt)

    def show_error_message(self, error_name):
        """ Tells if an error message should be shown in the template.
        """
        return error_name in self.errors

    def class_for_field(self, fieldname):
        """ Returns the class that should be applied to a field
        in the forms displayed by the product.
        """
        base_class = 'field'
        error_class = ' error'
        if not fieldname in self.error_mapping:
            if fieldname in self.errors:
                base_class += error_class
            return base_class

        for error_name in self.error_mapping[fieldname]:
            if self.show_error_message(error_name):
                return base_class + error_class
        return base_class

class RealURLView(BaseView):
    """ We need this view to build the 'send as pdf'
    action menu.    
    """
    def __call__(self):
        base = self.context.REQUEST['ACTUAL_URL']
        get_params = '&'.join(
            ['%s=%s' % (k, v) for k, v in self.context.REQUEST.form.items()])

        if get_params:
           base += '?' + get_params
        return base

class DownloadPDF(BaseView):
    """ View called when clicking the 'Click here to preview'
    link.
    """
    def __call__(self):
        form = self.request.form
        if not 'pdf_name' in form:
            # Should not happen.
            self.errors.append('file_not_specified')
            return self.index()

        filename = form['pdf_name']

        prefix = self.generate_filename_prefix()
        if not filename.startswith(prefix):
            # The user should not be able to see this file.
            raise Unauthorized()

        if not filename in os.listdir(self.tempdir):
            self.errors.append('file_not_found')
            self.request.response.setStatus(404)
            return self.index()

        self.pdf_file = file('%s/%s' % (self.tempdir, filename),
                             'r')
        self.request.response.setHeader("Content-type",
                                        "application/pdf")
        return self.pdf_file.read()

class SendForm(BaseView):
    """ If the user does not have Javascript enabled, he is
    redirected to this page.
    This page generates the PDF using the URL of the previous page
    and shows a form to send it by mail.

    It should logically show the same thing than the previous page
    (the user has no JS enabled so no funky stuff happened).
    The only case it could fail is if the previous page was processing a
    POST form. In this case, we can just render the page as if it was
    called with a simple GET request.
    """

    def get_page_source(self):
        """ Returns the HTML source of a web page, considering
        that the URL of the page is contained in the form under
        the 'page_url' key.
        """
        url = self.request.form['page_url']
        context_url = self.context.absolute_url()

        view_name, get_params = extract_from_url(url, context_url)

        # Now we will reinject the GET parameters in the request.
        if get_params:
            for key in get_params:
                self.request.form[key] = get_params[key]

        if not view_name:
            ttool = getToolByName(self.context, 'portal_types')
            if self.context.portal_type in ttool:
                context_type = ttool[self.context.portal_type]
                view_name = context_type.getProperty('immediate_view')

        try:
            view = self.context.restrictedTraverse(view_name)
        except:
            return

        return view()

    def generate_temp_filename(self):
        """ Generates the filename used to store the PDF file.
        Basically the md5 hash of th user's email followed
        by a timestamp.
        If the user is anonymous, just use the timestamp.
        In case of conflict, we just happen '-x' at the end.
        """
        prefix = self.generate_filename_prefix()
        now = datetime.now()
        # Ok that might not be the best timestamp system, but it's
        # enough for our needs.
        timestamp = ''.join([str(x) for x in now.timetuple()])
        filename = prefix + timestamp
        return find_filename(self.tempdir,
                             filename)

    def generate_pdf_file(self, source):
        """ Generates a PDF file from the given source
        (string containing the HTML source of a page).
        """
        filename = self.generate_temp_filename()
        if not filename:
            self.errors.append('filename_generation_failed')
            return

        try:
            transform_module = getattr(transforms, self.pdf_generator)
        except AttributeError:
            self.errors.append('wrong_generator_configuration')
            return

        self.filename = filename
        url = self.context.absolute_url()

        export_file, err = transform_module.html_to_pdf(source,
                                                        self.tempdir,
                                                        filename,
                                                        original_url = url)
        if err:
            self.errors.append('pdf_creation_failed')
            return

        self.pdf_file = export_file
        self.pdf_file.close()

    def check_form(self):
        """ Checks the form submitted when the user clicks on
        the 'send by mail' button.
        """
        form = self.request.form
        fields = ['name',
                  'name_recipient',
                  'email',
                  'email_recipient',
                  'title',
                  'content']

        # All fields are mandatory
        for field in fields:
            if not form.get(field):
                self.errors.append(field)

        # We check that emails are real emails.
        mail_validator = validation.validatorFor('isEmail')
        for field in ['email', 'email_recipient']:
            value = form.get(field)
            if not value:
                continue
            if not mail_validator(value) == 1:
                self.errors.append('invalid_' + field)

    def get_values(self):
        """ Provides the values used to fill the form.
        """
        if self.errors:
            return self.request.form

        values = {'filename': self.filename}
        if self.get_user():
            values['name'] = self.get_user_fullname()
            values['email'] = self.get_user_email()

        return values

    def process_form(self):
        """
        """
        form = self.request.form

        mfrom = '%s <%s>' % (form['name'],
                             form['email'])
        mto = '%s <%s>' % (form['name_recipient'],
                           form['email_recipient'])
        self.pdf_file = file('%s/%s' % (self.tempdir,
                                        form['filename']),
                             'r')
        send_message(mfrom,
                     mto,
                     form['title'],
                     form['content'],
                     self.pdf_file)

    def __call__(self):
        form = self.request.form

        if 'form_submitted' in form:
            # The user clicked on the 'send by mail'
            # button.
            self.check_form()
            if not self.errors:
                self.process_form()

                #XXX - show success messafe
            else:
                #XXX - show error message
                pass
        elif 'form_cancelled' in form:
            # The user clicked on the 'cancel' button.

            #XXX - redirect to the previous page.
            pass
        else:
            # The user clicked on the 'send by mail'
            # link.
            if not 'page_url' in form:
                self.errors.append('no_source')
            else:
                source = self.get_page_source()
                self.generate_pdf_file(source)

        return self.index()
                

class SendFormAjax(SendForm):
    """ This class contains a set of methods that are called
    with jquery.pyproxy.
    """

    
    def generate_pdf(self):
        """ This jquery action is called when clicking on the
        'send by mail' button.
        The submitted form contains only one field called 'page',
        which contains the HTML source of the page that the user
        was seeing.
        """
        form = self.request.form

        if not 'page' in form:
            # Should not happen.
            return
