# Defines the html_to_pdf method using WKHTMLTOPDF:
# http://code.google.com/p/wkhtmltopdf/
import os
import subprocess
import logging

from Products.CMFPlone.utils import safe_unicode

from collective.sendaspdf.utils import find_filename
from collective.sendaspdf.emailer import su, get_charset

logger = logging.getLogger('collective.sendaspdf')

wk_command = os.environ.get('WKHTMLTOPDF_PATH')
if wk_command:
    logger.info('wkhtmltopdf found at  %s: ' % wk_command)
else:
    wk_command = 'wkhtmltopdf'
    logger.warn("wkhtmltopdf path unknown, hope it's in the path")

simple_options = ['book', 'collate',
                  'disable-external-links', 'disable-internal-links',
                  'disable-pdf-compression', 'disable-smart-shrinking',
                  'forms', 'grayscale', 'lowquality', 'no-background',
                  'header-line', 'footer-line',
                  'toc', 'toc-disable-back-links', 'toc-disable-links']
                  
valued_options = ['copies', 'cover', 'dpi',  
                  'margin-top','margin-bottom', 'margin-left', 'margin-right',
                  'minimum-font-size', 'orientation',
                  'page-height', 'page-offset', 'page-size', 'page-width',
                  'header-font-name', 'header-html', 'header-font-size', 'header-spacing',
                  'header-left', 'header-center','header-right', 
                  'footer-font-name', 'footer-html', 'footer-font-size', 'footer-spacing',
                  'footer-left', 'footer-center','footer-right', 
                  'toc-depth', 'toc-header-text']
                  

def html_to_pdf(source, export_dir, filename,
                original_url, use_print_css, extra_options=[]):
    # First we need to store the source in a temporary
    # file.
    html_filename = find_filename(export_dir,
                                  filename,
                                  'html')
    if not html_filename:
        return None, ['no_filename_temp_html']

    try:
        source = source.encode('utf8')
    except UnicodeDecodeError:
        # When the source is sent through Ajax, it's already decoded
        # and causes an error here.
        pass

    html_file = file('%s/%s' % (export_dir, html_filename),
                     'wb')

    html_file.write(source)
    html_file.close()

    # Run the wkhtmltopdf command.
    args = [wk_command,
            '--disable-javascript',
            'file://%s/%s' % (export_dir, html_filename),
            '%s/%s' % (export_dir, filename)]

    if use_print_css:
        args.insert(2, '--print-media-type')

    for opt in extra_options:
        args.insert(2, opt)

    try:
        p = subprocess.Popen(args)
        p.wait()
    except:
        logger.error('Running wkhtmltopdf failed. Please check that ' + \
                     'you use a version compatible with your OS and ' + \
                     'the version is 0.9.')
        return None, ['pdf_generation_failed']

    os.remove('%s/%s' % (export_dir, html_filename))
    pdf_file = file('%s/%s' % (export_dir, filename),
                    'r')
    return pdf_file, None
