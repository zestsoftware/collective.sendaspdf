from zope.component import adapts
from zope.interface import implements
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody
from collective.sendaspdf.tool import ISendAsPDFTool

class SendAsPdfToolXMLAdapter(XMLAdapterBase):
    adapts(ISendAsPDFTool, ISetupEnviron)


    _LOGGER_ID = 'sendaspdf'

    name = 'sendaspdftool'

    exportfield = {
        'pdf_generator': (lambda x : str(x),
                          lambda x : x),
        'tempdir':(lambda x : str(x),
                   lambda x : x),
        'excluded_browser_attachment': (lambda x : ';'.join(x),
                                        lambda x : tuple(x.split(';'))),
        'salt':(lambda x : str(x),
                lambda x : x),
        'mail_title':(lambda x : str(x),
                      lambda x : x),
        'mail_content':(lambda x : str(x),
                        lambda x : x),
        'filename_in_mail':(lambda x : str(x),
                            lambda x : x),
        'always_print_css':(lambda x : str(x),
                            lambda x : bool(x)),
        'print_css_types':(lambda x : ';'.join(x),
                           lambda x : tuple(x.split(';')))
        }


    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractPredicates())

        self._logger.info('Send as pdf tool exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgePredicates()

        self._initPredicates(node)

        self._logger.info('Send as pdf tool imported.')

    def _extractPredicates(self):
        fragment = self._doc.createDocumentFragment()
        
        for k, functions in self.exportfield.iteritems():
            serialize = functions[0]
            v = serialize(self.context[k])
            child = self._doc.createElement('property')
            child.setAttribute('name', k)
            child.setAttribute('value', v)
            fragment.appendChild(child)
        
        return fragment

    def _purgePredicates(self):
        self.context.__init__()

    def _initPredicates(self, node):
        out = {}
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue
            parent = self.context

            name = child.getAttribute('name')
            if name in self.exportfield:
                deserialize = self.exportfield[name][1]
                value = deserialize(child.getAttribute('value'))
                out[str(name)] = value

        self.context.update(**out)

def importProviders(context):
    """Import actions tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_sendaspdf', None)
    if tool is None:
        logger = context.getLogger('sendaspdf')
        logger.debug('Nothing to import.')
        return

    importObjects(tool, '', context)

def exportProviders(context):
    """Export actions tool.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_sendaspdf', None)
    if tool is None:
        logger = context.getLogger('sendaspdf')
        logger.debug('Nothing to export.')
        return
    exportObjects(tool, '', context)
