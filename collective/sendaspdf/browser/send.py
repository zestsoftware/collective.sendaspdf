import os
from datetime import datetime

import ho.pisa as pisa

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS

from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string

from collective.sendaspdf.utils import md5_hash, extract_from_url

class SendByMail(BrowserView):
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
    def __init__(self, *args, **kwargs):
        """ We just need to define some instance variables.
        """
        super(SendByMail, self).__init__(*args, **kwargs)

        # The list of errors found when checking the form.
        self.errors = []

        # XXX - this should be changed in the future,
        # using site properties so the users can manage this
        # from the ZMI.
        self.tempdir = '/tmp/' #XXX - use tempdir
        self.salt = 'kikoo'
        self.filename_in_mail = 'screenshot'

        self.pdf_file = None

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
            default_view = self.context.defaultView()
            if default_view in self.context:
                view = self.context[default_view]
        else:
            try:
                view = self.context.restrictedTraverse('@@' + view_name)
            except:
                view = self.context

        return view()

    def get_user_email(self):
        """ Returns the currently logged-in user's email.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            return

        member = mtool.getAuthenticatedUser()
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

        try:
            files = os.listdir(self.tempdir)
        except:
            # This shall not happen, except if the tempdir has not
            # been set correctly.
            return

        # We check the file name is not already used in the tempdir.
        # If so, we try to prepend a number at the end.
        if filename + '.pdf' in files:
            postfix = 0
            while postfix <= RENAME_AFTER_CREATION_ATTEMPTS:
                if '%s_%s.pdf' % (filename, postfix) in files:
                    postfix += 1
                    continue

                filename = '%s_%s' % (filename, postfix)
                break

            if postfix > RENAME_AFTER_CREATION_ATTEMPTS:
                return

        return filename + '.pdf'

    def generate_pdf_file(self, source):
        """ Generates a PDF file from the given source
        (string containing the HTML source of a page).
        """
        filename = self.generate_temp_filename()
        if not filename:
            self.errors.append('filename_generation_failed')
            return

        file_path = '%s/%s' % (self.tempdir, filename)
        self.pdf_file = file(file_path, "wb")

        url = self.context.absolute_url()
        pdf = pisa.CreatePDF(
            str(source.encode('ascii', 'replace')),
            self.pdf_file,
            log_warn = 1,
            log_err = 1,
            path = url,
            link_callback = pisa.pisaLinkLoader(url).getFileName,
            )
        self.pdf_file.close()

        if pdf.err:
            self.errors.append('pdf_creation_failed')

    def check_form(self):
        """ Checks the form submitted when the user clicks on
        the 'send by mail' button.
        """
        

    def process_form(self):
        """ Process the submitted form.
        """

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
                

class SendByMailAjax(SendByMail):
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
