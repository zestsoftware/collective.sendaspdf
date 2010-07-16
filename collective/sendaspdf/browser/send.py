from AccessControl import Unauthorized
from Products.validation import validation
from Products.CMFCore.utils import getToolByName

from collective.sendaspdf.emailer import send_message

from collective.sendaspdf.browser.base import BaseView

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
    error_mapping = {'email': ['email', 'invalid_email'],
                     'email_recipient': ['email_recipient',
                                         'invalid_email_recipient']}

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
            self.make_pdf()

        return self.index()
