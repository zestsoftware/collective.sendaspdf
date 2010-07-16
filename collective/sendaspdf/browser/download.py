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
            return self.index()

        self.request.form['pdf_name'] = self.filename
        return self.context.restrictedTraverse('@@send_as_pdf_download')()

class DownloadPDF(BaseView):
    """ View called when clicking the 'Click here to preview'
    link.
    """
    def __call__(self):
        form = self.request.form
        if not 'pdf_name' in form:
            # Should not happen.
            self.errors.append('file_not_specified')
            return self.index()

        filename = form['pdf_name']

        prefix = self.generate_filename_prefix()
        if not filename.startswith(prefix):
            # The user should not be able to see this file.
            raise Unauthorized()

        if not filename in os.listdir(self.tempdir):
            self.errors.append('file_not_found')
            self.request.response.setStatus(404)
            return self.index()

        self.pdf_file = file('%s/%s' % (self.tempdir, filename),
                             'r')
        self.request.response.setHeader("Content-type",
                                        "application/pdf")
        return self.pdf_file.read()
