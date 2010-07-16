  # -*- extra stuff goes here -*- 
from zope.i18nmessageid import MessageFactory
SendAsPDFMessageFactory = MessageFactory(u'collective.sendaspdf')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
