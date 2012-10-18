# This file is taken from Products.PasswordResetTool
# We copied it here to avoid test problems is the product
# is not installed in the buildout.
# The product can be found here: http://plone.org/products/passwordresettool

from datetime import datetime, timedelta

from Products.Five.browser import BrowserView
from Products.SecureMailHost.SecureMailHost import SecureMailHost as MailBase

class LongView(BrowserView):
    """ A view that takes a loooooong time
    to answer (well, about 20 seconds).
    Used to ensure we correctly kill wkhtmltopdf
    when it takes too long to finish its job (that may lead
    to lock the Zope thread and getting wkhtmltopdf
    unusable until the next restart of the instance).
    """

    def wait(self):
        end_time = datetime.now() + timedelta(0.0002)
        while datetime.now() < end_time:
            pass

        return 'Ho, finished :)'

class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.

    Thanks to Rocky Burt for inspiration.
    """

    def __init__(self, id):
        MailBase.__init__(self, id, smtp_notls=True)
        self.reset()

    def reset(self):
        self.messages = []

    def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
        """
        Basically construct an email.Message from the given params to make sure
        everything is ok and store the results in the messages instance var.
        """
        self.messages.append(message)

    def secureSend(self, message, mto, mfrom, **kwargs):
        kwargs['debug'] = True
        result = MailBase.secureSend(self, message=message, mto=mto,
                                     mfrom=mfrom, **kwargs)
        self.messages.append(result)

    def validateSingleEmailAddress(self, address):
        return True # why not
