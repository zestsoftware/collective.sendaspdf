# This package defines transformers for html to pdf.
# Each module defines a html_to_pdf method that takes three parameters:
# - source: the HTML source
# - export_dir: path to the directory where the PDF will be created.
# - filename: the name of the file (it the name does not end with '.pdf',
#   the method will add it.
# - original_url: the URL of the file being transformed.
#
# Methods returns a <file> object and a list of potential errors.

import pisa, wk
