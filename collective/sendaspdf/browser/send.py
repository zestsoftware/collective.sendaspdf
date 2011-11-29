from zope.i18n import translate
from AccessControl import Unauthorized
from Products.validation import validation
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from collective.sendaspdf.emailer import send_message

from collective.sendaspdf import SendAsPDFMessageFactory as _
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
                                         'invalid_email_recipient'],
                     'pdf_name': ['file_not_found',
                                  'file_not_specified',
                                  'file_unauthorized']}

    def check_form(self):
        """ Checks the form submitted when the user clicks on
        the 'send by mail' button.
        """
        form = self.request.form
        user = self.get_user()
        self.check_pdf_accessibility()

        fields = ['name_recipient',
                  'email_recipient',
                  'title',
                  'text']
        if not user:
            fields.extend(['name', 'email'])

        # All fields are mandatory
        for field in fields:
            if not form.get(field):
                self.errors.append(field)

        # We check that emails are real emails.
        email_validator = validation.validatorFor('isEmail')
        email_fields = ['email_recipient']
        if not user:
            email_fields.append('email')

        for field in email_fields:
            value = form.get(field)
            if not value:
                continue
            if not email_validator(value) == 1:
                self.errors.append('invalid_' + field)

    def get_values(self):
        """ Provides the values used to fill the form.
        """
        if self.errors:
            return self.request.form

        values = {'pdf_name': self.filename}

        values['title'] = self.pdf_tool.mail_title
        values['text'] = self.pdf_tool.mail_content

        if self.get_user():
            values['name'] = self.get_user_fullname()
            values['email'] = self.get_user_email()

        return values

    def process_form(self):
        """
        """
        form = self.request.form        

        if self.get_user():
            mfrom = '%s <%s>' % (self.get_user_fullname(),
                                 self.get_user_email())
        else:
            mfrom = '%s <%s>' % (form['name'],
                                 form['email'])

        mto = '%s <%s>' % (form['name_recipient'],
                           form['email_recipient'])
        pdf_file = file('%s/%s' % (self.tempdir,
                                   form['pdf_name']),
                        'r')
        send_message(mfrom,
                     mto,
                     form['title'],
                     form['text'],
                     pdf_file,
                     self.pdf_tool.filename_in_mail)

    def get_editor(self):
        """ Get's the editor to use in the send form.
        """
        memberdata = getToolByName(self.context,
                                   'portal_memberdata')
        default_editor = memberdata.get('wysiwyg_editor', None)

        if not default_editor:
            # In Plone4, default editor is in
            # portal_properties/site_properties/default_editor.
            portal_props = getToolByName(self.context,
                                         'portal_properties')
            try:
                default_editor = portal_props.site_properties.default_editor
            except AttributeError:
                default_editor = 'plone_wysiwyg'

        portal_membership = getToolByName(self.context,
                                          'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        if member:
            member_editor = member.getProperty('wysiwyg_editor',
                                       default_editor)
        editor =  member_editor or default_editor
        return editor.lower()

    def __call__(self):
        form = self.request.form

        if 'form_submitted' in form:
            # The user clicked on the 'send by mail'
            # button.
            self.check_form()
            if not self.errors:
                self.process_form()
                msg = _(u'msg_success',
                        default=u'The e-mail has been sent')
                msg_type = 'info'
            else:
                msg = _(u'msg_error',
                        default=u'Errors appeared while processing your form')
                msg_type = 'error'
                

            self.context.plone_utils.addPortalMessage(
                translate(msg,
                          target_language=self.get_lang()),
                type=msg_type)

            if not self.errors:
                self.request.response.redirect(self.context.absolute_url())

        elif 'form_cancelled' in form:
            # The user clicked on the 'cancel' button.
            self.request.response.redirect(self.context.absolute_url())
        else:
            # The user clicked on the 'send by mail'
            # link.
            self.make_pdf()
            if self.errors:
                # The PDF generation did not work, we render the page
                # used when errors are found when sending the mail.
                self.index = ZopeTwoPageTemplateFile('templates/download.pt')

        # We need the self parameter for Plone 4
        return self.index(self)
