from zope.interface import Interface

class ISendAsPDFOptionsMaker(Interface):
    """ 
    """

    def overrideAll():
        """ Returns a boolean telling if the options
        specified by the adapter should override the settings
        provided by the user or specified in the request.
        """

    def getOptions(context = None):
        """ Returns a dictionary of options that will be applied
        to generated PDF.
        """
