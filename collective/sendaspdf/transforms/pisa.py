# Defines the html_to_pdf method using PISA:
# http://github.com/holtwick/xhtml2pdf

simple_options = []
valued_options = []


def html_to_pdf(source, export_dir, filename, original_url,
                use_print_css, extra_options=[]):
    # We import pisa inside the function so it does not raise
    # import exception if pisa is not installed.
    try:
        # First try newer version of library under a different name.
        import xhtml2pdf.pisa as pisa
        pisa  # pyflakes
    except ImportError:
        # Try the old library.  Note that you can also get the above
        # ImportError simply because you are on Python 2.4 and
        # xhtml2pdf.pisa tries and fails to import hashlib.
        import ho.pisa as pisa

    file_path = '%s/%s' % (export_dir, filename)

    pdf_file = file(file_path, "wb")
    link_callback = pisa.pisaLinkLoader(original_url).getFileName

    pdf = pisa.CreatePDF(source,
                         pdf_file,
                         log_warn=1,
                         log_err=1,
                         path=original_url,
                         link_callback=link_callback,
                         )

    if pdf.err:
        return None, pdf.err

    return pdf_file, None
