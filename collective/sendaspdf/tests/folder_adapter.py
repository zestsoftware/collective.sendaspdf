from zope import component
from zope.interface import implements
from OFS.interfaces import IFolder

from collective.sendaspdf.interfaces import ISendAsPDFOptionsMaker

class FolderOptionsMaker(object):
    implements(ISendAsPDFOptionsMaker)
    component.adapts(IFolder)

    def __init__(self, context):
        self.context = context

    def overrideAll(self):
        return False

    def getOptions(self):
        return {'header-center': 'This was added by a custom adapter',
                'margin-top': 42,
                'footer-center': self.context.title,
                'book': 1,
                '--no-toc': 1}
