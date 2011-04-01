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

def html_to_pdf(source, export_dir, filename, original_url, use_print_css):
    # First we need to store the source in a temporary
    # file.
    html_filename = find_filename(export_dir,
                                  filename,
                                  'html')
    if not html_filename:
        return None, ['no_filename_temp_html']

    html_file = file('%s/%s' % (export_dir, html_filename),
                     'wb')

    html_file.write(source)

    html_file.close()

    # Run the wkhtmltopdf command.
    args = [wk_command,
            'file://%s/%s' % (export_dir, html_filename),
            '%s/%s' % (export_dir, filename),
            '--disable-javascript',
            '--ignore-load-errors']
    if use_print_css:
        args.append('--print-media-type')

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
