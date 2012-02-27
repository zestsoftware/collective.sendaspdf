from zope.interface import Interface

class ISendAsPDFOptionsMaker(Interface):
    """
    """

    def getOptions(context = None):
        """ Returns a dictionary of options that will be applied
        to generated PDF.
        """
