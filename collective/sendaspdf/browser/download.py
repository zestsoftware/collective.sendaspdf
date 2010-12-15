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
        return self.pdf_file.read()
