import os
from AccessControl import Unauthorized

from collective.sendaspdf.browser.base import BaseView


class PreDownloadPDF(BaseView):
    """ This page is the one called when clicking on the
    'Download as PDF' view.
    It generates the PDF file then redirects to the real
    download view (see below).
    """
    def __call__(self):
        self.make_pdf()
        if self.errors:
            return self.index(self)

        self.request.form['pdf_name'] = self.filename
        return self.context.restrictedTraverse('@@send_as_pdf_download')()

class DownloadPDF(BaseView):
    """ View called when clicking the 'Click here to preview'
    link.
    """
    def generate_pdf_name(self):
        """ Generates the name for the PDF file.
        If the context title does not contain non-ascii characters,
        we'll use it.
        Otherwise we'll rewrite it using normalize string.
        """
        try:
            name = self.context.title.encode('ascii')
        except (UnicodeDecodeError, UnicodeEncodeError, ):
            name = self.context.id

        return '%s.pdf' % name

    
    def __call__(self):
        form = self.request.form
        self.check_pdf_accessibility()

        if self.errors:
             return self.index(self)

        self.pdf_file = file('%s/%s' % (self.tempdir,
                                        form['pdf_name']),
                             'r')
        self.request.response.setHeader("Content-type",
                                        "application/pdf")
        self.request.response.setHeader("X-Robots-Tag",
                                        "noindex")
        self.request.response.setHeader("Cache-Control",
                                        "no-cache, must-revalidate")

        if not self.pdf_tool.is_browser_excluded(self.request['HTTP_USER_AGENT']):
            disposition = 'attachment; filename="%s"' % self.generate_pdf_name()
            self.request.response.setHeader('Content-Disposition', disposition)

        return self.pdf_file.read()
