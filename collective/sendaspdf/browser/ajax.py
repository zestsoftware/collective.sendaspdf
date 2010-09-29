from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string

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

        if not 'page' in form:
            # This should not happen.
            return jq

        self.make_pdf()
        return jq
        if self.errors:
            self.index = ZopeTwoPageTemplateFile('templates/ajax_error.pt')
        else:
            self.index = ZopeTwoPageTemplateFile('templates/ajax_form.pt')

        return jq

    @jquery
    def show_send_form(self):
        # It's just to be able to use @@reload without being bothered
        # by the decorator.
        return self._show_send_form()
