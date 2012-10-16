  # -*- extra stuff goes here -*- 
try:
    from zope.i18nmessageid import MessageFactory
    SendAsPDFMessageFactory = MessageFactory(u'collective.sendaspdf')
except ImportError:
    # Might happen with the worker, we do not really care.
    pass


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
