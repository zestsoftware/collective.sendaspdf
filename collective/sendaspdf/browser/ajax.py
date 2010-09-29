from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate

from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string

from collective.sendaspdf import SendAsPDFMessageFactory as _
from collective.sendaspdf.browser.send import SendForm

class SendFormAjax(SendForm):
    """ This class contains a set of methods that are called
    with jquery.pyproxy.
    """

    def get_page_source(self):
        """ We override the get_page_source has this is
        sent by the ajax request.
        """
        return self.request.form.get('page', '')

    def _show_send_form(self):
        form = self.request.form

        jq = JQueryProxy()
        jq.extend_grammar({'send_as_pdf_lightbox': []});

        if not 'page' in form:
            # This should not happen.
            return jq

        self.make_pdf()
        if self.errors:
            self.index = ZopeTwoPageTemplateFile('templates/ajax.pt')
        else:
            self.index = ZopeTwoPageTemplateFile('templates/send_form.pt')
        
        jq('#send_as_pdf_popup').remove()
        jq('body').append('<div id="send_as_pdf_popup"></div>')
        jq('#send_as_pdf_popup').html(clean_string(self.index()))
        jq('#send_as_pdf_popup').send_as_pdf_lightbox()
        return jq

    @jquery
    def show_send_form(self):
        # It's just to be able to use @@reload without being bothered
        # by the decorator.
        return self._show_send_form()

    def _send_mail(self):
        jq = JQueryProxy()
        self.check_form()

        if not self.errors:
            self.process_form()
            self.index = ZopeTwoPageTemplateFile('templates/ajax.pt')
            jq('#send_as_pdf_popup').html(clean_string(self.index()))
        else:
            print self.errors
            # First update the fields class.
            for field in ['name_recipient',
                          'email_recipient',
                          'title',
                          'content',
                          'name',
                          'email']:

                if 'error' in self.class_for_field(field):
                    jq('#field_' + field).addClass('error')
                else:
                    jq('#field_' + field).removeClass('error')

            # We hide the previous errors.
            jq('.error_msg').addClass('dont-show');
            jq('.error_msg').removeClass('error_msg');
            
            for error in self.errors:
                jq('#error_' + error).removeClass('dont-show')
                jq('#error_' + error).addClass('error_msg')

        return jq

    @jquery
    def send_mail(self):
        return self._send_mail()
