from AccessControl import Unauthorized
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from Products.Archetypes import atapi
from Products.CMFCore.utils import ImmutableId
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema

import config

from collective.sendaspdf import SendAsPDFMessageFactory as _

sendAsPDFSchema = ATDocumentSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'pdf_generator',
        default='pisa',
        widget=atapi.SelectionWidget(
            format="select",
            label=_(u'label_pdf_generator',
                    default=u'PDF generator'),
            ),
        vocabulary = '_generatorVocabulary'
        ),
    atapi.StringField(
        name = 'tempdir',
        default='/tmp',
        widget=atapi.StringWidget(
            label=_(u'label_export_dir',
                    default=u'Directory where PDF files will be stored'),
            ),
        ),
    atapi.StringField(
        name = 'salt',
        default='salt_as_pdf',
        widget=atapi.StringWidget(
            label=_(u'label_salt',
                    default=u'SALT used when hasing users\' e-mails'),
            ),
        ),
    atapi.StringField(
        name = 'filename_in_mail',
        default='screenshot.pdf',
        widget=atapi.StringWidget(
            label=_(u'label_filename_title',
                    default=u'Name of the PDF file in the mail'),
            ),
        ),
    atapi.StringField(
        name = 'mail_title',
        widget=atapi.StringWidget(
            label=_(u'label_mail_title',
                    default=u'Default title of e-mails'),
            ),
        ),
    atapi.TextField(
        name = 'mail_content',
        widget=atapi.RichWidget(
            label=_(u'label_mail_content',
                    default=u'Default body of e-mails'),
            ),
        ),
    atapi.BooleanField(
        name='always_print_css',
        widget=atapi.BooleanWidget(
            label=_(u'label_print_css_always',
                    default=u'Always use print CSS'),
            description=_(u'help_print_css_always',
                          default=u'Always use the print CSS (only valid' + \
                          'with wkhtmltopdf, xhtml2pdf will use the ' + \
                          'print CSS whatever you chose')
            ),
        ),
    atapi.LinesField(
        name='print_css_types',
        widget=atapi.LinesWidget(
            label=_(u'label_print_css',
                    default=u'Portal types using print css'),
            description=_(u'help_print_css',
                          default=u'You can register here a list of portal ' + \
                          'types for which the system must use the print ' + \
                          'CSS instead of the scrren one (currently only ' + \
                          'working if you use wkhtmltopdf. xhtml2pdf uses ' + \
                          'the print CSS by default). One type per line'),
        ),
    ),

))

for field in ['title', 'description', 'text']:
    if field in sendAsPDFSchema:
        sendAsPDFSchema[field].widget.visible={'edit': 'invisible',
                                               'view': 'invisible'}

class SendAsPDFTool(ImmutableId, ATDocument):
    """ Tool for sendaspdf product.
    Allows to set various settings:
    - the PDF generator used.
    - the directory to store PDF files.
    - the SALT used in md5 hashing
    - the default title for the mail
    - the default body of the mail
    """
    security = ClassSecurityInfo()
    __implements__ = (atapi.BaseFolder.__implements__, )

    id = 'portal_sendaspdf'
    typeDescription = "Configure send as pdf"
    typeDescMsgId = 'description_edit_sendaspdftool'
    schema = sendAsPDFSchema

    def __init__(self, *args, **kwargs):
        self.setTitle('Send as PDF configuration')

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self, skip_self=False):
        pass

    security.declarePublic('_genderVocabulary')
    def _generatorVocabulary(self):
        return atapi.DisplayList([
                ('pisa',
                 _(u'label_pisa',
                   default=u'XHTML2PDF: HTML/CSS to PDF converter written ' + \
                   'in Python (http://www.xhtml2pdf.com/')),
                ('wk',
                 _(u'label_wk',
                   default=u'wkhtmltopdf: Simple shell utility to convert ' + \
                   'html to pdf using the webkit (Safari, Chrome) rendering ' + \
                   'engine (http://code.google.com/p/wkhtmltopdf/)')),
            ])


atapi.registerType(SendAsPDFTool, config.PROJECTNAME)
