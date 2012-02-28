# Defines the html_to_pdf method using PISA:
# http://github.com/holtwick/xhtml2pdf

simple_options = []
valued_options = []

def html_to_pdf(source, export_dir, filename, original_url, use_print_css, extra_options=[]):
    # We import pisa inside the function so it does not raise
    # import exception if pisa is not installed.
    import ho.pisa as pisa
    
    file_path = '%s/%s' % (export_dir, filename)

    pdf_file = file(file_path, "wb")
    pdf = pisa.CreatePDF(
        str(source.encode('ascii', 'replace')),
        pdf_file,
        log_warn = 1,
        log_err = 1,
        path = original_url,
        link_callback = pisa.pisaLinkLoader(original_url).getFileName,
        )

    if pdf.err:
        return None, pdf.err

    return pdf_file, None
