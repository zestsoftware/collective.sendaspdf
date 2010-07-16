from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string


from collective.sendaspdf.browser.send import SendForm

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
