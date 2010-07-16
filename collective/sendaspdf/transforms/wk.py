# Defines the html_to_pdf method using WKHTMLTOPDF:
# http://code.google.com/p/wkhtmltopdf/
import os
import subprocess

from collective.sendaspdf.utils import find_filename
from collective.sendaspdf.emailer import su, get_charset

def html_to_pdf(source, export_dir, filename, original_url):
    # First we need to store the source in a temporary
    # file.
    html_filename = find_filename(export_dir,
                                  filename,
                                  'html')
    if not html_filename:
        return None, ['no_filename_temp_html']

    html_file = file('%s/%s' % (export_dir, html_filename),
                     'wb')
    html_file.write(str(source.encode('ascii',
                                      'ignore')))
    html_file.close()

    # Run the wkhtmltopdf command.
    args = ['wkhtmltopdf',
            'file://%s/%s' % (export_dir, html_filename),
            '%s/%s' % (export_dir, filename),
            '--disable-javascript',
            '--ignore-load-errors']
    p = subprocess.Popen(args)

    pdf_file = file('%s/%s' % (export_dir, filename),
                    'wb')
    return pdf_file, None
