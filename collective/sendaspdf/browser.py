from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string

class SendByMail(BrowerView):
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

        
