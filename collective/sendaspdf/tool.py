import os
from datetime import datetime

from zope.i18n import translate
from AccessControl import Unauthorized
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from Products.Archetypes import atapi
from Products.CMFCore.utils import ImmutableId
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from zope.interface import Interface, implements
import config

from collective.sendaspdf import SendAsPDFMessageFactory as _

class ISendAsPDFTool(Interface):
    """send as pdf tool marker interface"""


sendAsPDFSchema = ATDocumentSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'pdf_generator',
        default='wk',
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

    atapi.LinesField(
        name = 'excluded_browser_attachment',
        default=[],
        widget=atapi.LinesWidget(
            label=_(u'label_excluded_browsersattachments',
                    default=u'List of browsers for which PDF ' + \
                    'filename will not be forced'),
            description=_(u'label_help_excluded_attachments',
                          default=u'Browsers might warn the user ' +\
                          'that downloading the PDF might harm their computer. ' +\
                          'You can set here a list of browser for which the system will ' + \
                          'not force the download. We recommend to have Chrome in the list')
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
        name = 'mail_title',
        widget=atapi.StringWidget(
            label=_(u'label_mail_title',
                    default=u'Default title of e-mails'),
            ),
        schemata='mail',
        ),

    atapi.TextField(
        name = 'mail_content',
        default_content_type='text/html',
        allowable_content_types=('text/html', ),
        widget=atapi.RichWidget(
            label=_(u'label_mail_content',
                    default=u'Default body of e-mails'),
            ),
        schemata='mail',
        ),

    atapi.StringField(
        name = 'filename_in_mail',
        default='screenshot.pdf',
        widget=atapi.StringWidget(
            label=_(u'label_filename_title',
                    default=u'Name of the PDF file in the mail'),
            ),
        schemata='mail',
        ),

    atapi.BooleanField(
        name='always_print_css',
        widget=atapi.BooleanWidget(
            label=_(u'label_print_css_always',
                    default=u'Always use print CSS'),
            description=_(u'help_print_css_always',
                          default=u'Always use the print CSS (only valid' + \
                          'with wkhtmltopdf, xhtml2pdf will use the ' + \
                          'print CSS whatever you chose)')
            ),
        schemata='wk',
        ),

    atapi.LinesField(
        name='print_css_types',
        widget=atapi.LinesWidget(
            label=_(u'label_print_css',
                    default=u'Portal types using print css'),
            description=_(u'help_print_css',
                          default=u'You can register here a list of portal ' + \
                          'types for which the system must use the print ' + \
                          'CSS instead of the screen one (currently only ' + \
                          'working if you use wkhtmltopdf. xhtml2pdf uses ' + \
                          'the print CSS by default). One type per line'),
        ),
        schemata='wk',
    ),

    atapi.BooleanField(
        name='use_book_style',
        widget=atapi.BooleanWidget(
            label=_(u'label_use_book_style',
                    default=u'Use book style'),
            description=_(u'help_use_book_style',
                          default=u'PDf generated will have a book ' + \
                          'style (will override custom margins)')
            ),
        schemata='wk',
        ),

    atapi.BooleanField(
        name='generate_toc',
        widget=atapi.BooleanWidget(
            label=_(u'label_add_toc',
                    default=u'Add table of contents'),
            description=_(u'help_add_toc',
                          default=u'A table of contents will be ' + \
                          'prepended to the generated files.')
            ),
        schemata='wk',
        ),

    atapi.IntegerField(
        name='margin_top',
        default = 10,
        widget=atapi.IntegerWidget(
            label=_(u'label_margin_top',
                    default=u'Margin top'),
            ),
        schemata='wk',
        ),

    atapi.IntegerField(
        name='margin_right',
        default = 10,
        widget=atapi.IntegerWidget(
            label=_(u'label_margin_right',
                    default=u'Margin right'),
            ),
        schemata='wk',
        ),

    atapi.IntegerField(
        name='margin_bottom',
        default = 10,
        widget=atapi.IntegerWidget(
            label=_(u'label_margin_bottom',
                    default=u'Margin bottom'),
            ),
        schemata='wk',
        ),

    atapi.IntegerField(
        name='margin_left',
        default = 10,
        widget=atapi.IntegerWidget(
            label=_(u'label_margin_left',
                    default=u'Margin left'),
            ),
        schemata='wk',
        ),

))

# Hides the default fields.
for field in ['title', 'description', 'text']:
    if field in sendAsPDFSchema:
        sendAsPDFSchema[field].widget.visible={'edit': 'invisible',
                                               'view': 'invisible'}

# Hides the fields other than the ones we defined.
for key in sendAsPDFSchema.keys():
    if sendAsPDFSchema[key].schemata not in ['default', 'mail', 'wk']:
        sendAsPDFSchema[key].widget.visible={'edit': 'invisible',
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
    __implements__ = ()
    implements(ISendAsPDFTool)
    
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
                   'in Python (http://www.xhtml2pdf.com/)')),
                ('wk',
                 _(u'label_wk',
                   default=u'wkhtmltopdf: Simple shell utility to convert ' + \
                   'html to pdf using the webkit (Safari, Chrome) rendering ' + \
                   'engine (http://code.google.com/p/wkhtmltopdf/)')),
            ])

    def _getMetadata(self):
        """ Gets the annotations linked to the tool.
        """
        anno_key = 'collective.sendaspdf'
        annotations = IAnnotations(self)
        
        metadata = annotations.get(anno_key,
                                   None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        return metadata

    def getPDFList(self):
        """ Gets the list of PDF generated by the product.
        """
        metadata = self._getMetadata()
        if not 'pdf_files' in metadata:
            metadata['pdf_files'] = PersistentDict()

        return metadata['pdf_files']

    def setPDFList(self, new_list):
        metadata = self._getMetadata()
        metadata['pdf_files'] = new_list

    def get_last_clean(self):
        metadata = self._getMetadata()
        if not 'last_clean' in metadata:
            metadata['last_clean'] = datetime.now()

        return metadata['last_clean']

    def registerPDF(self, filename):
        """ Registers a PDF filename in the list.
        """
        now = datetime.now()
        pdfs = self.getPDFList()
        pdfs[filename] = now

        if (now - self.get_last_clean()).seconds > 1000:
            self.cleanPDFs()

    def cleanPDFs(self):
        """ Removes from the filesystem the list of PDF
        files generated more than 2 hours ago.
        """
        to_delete = []
        pdfs = self.getPDFList()
        now = datetime.now()

        # First we compute the list of files to delete.
        for filename in pdfs:
            filedate = pdfs[filename]
            delta = now - filedate

            if delta.seconds > 7200:
                to_delete.append(filename)

        existing_files = os.listdir(self.tempdir)
        for filename in to_delete:
            del pdfs[filename]
            if filename in existing_files:
                os.remove('%s/%s' % (self.tempdir,
                                     filename))
        self.setPDFList(pdfs)
        metadata = self._getMetadata()
        metadata['last_clean'] = now

    def is_browser_excluded(self, browser_name):
        """ Returns True if the browser id (got from
        the user agent) falls under a rule in
        'excluded_browser_attachment'
        """
        for excluded in self.getExcluded_browser_attachment():
            if excluded in browser_name:
                return True

        return False

    def make_options(self):
        """ Returns a dictionnary of options that can be used in
        the tool.
        """
        if self.pdf_generator == 'pisa':
            return {}

        toc_msg = _(u'label_toc',
                    default = u'Table of content')

        return {'book': self.getUse_book_style(),
                'toc': self.getGenerate_toc(),
                'margin-top': self.getMargin_top(),
                'margin-right': self.getMargin_right(),
                'margin-bottom': self.getMargin_bottom(),
                'margin-left': self.getMargin_left(),
                'toc-header-text': translate(toc_msg, context = self.REQUEST)}

atapi.registerType(SendAsPDFTool, config.PROJECTNAME)
