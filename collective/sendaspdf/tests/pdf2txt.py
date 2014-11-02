# Code taken from PDFMiner tool pdf2txt:
# https://github.com/euske/pdfminer/blob/master/tools/pdf2txt.py

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from StringIO import StringIO


def display_pdf(content):
    fp = StringIO(content)
    codec = 'utf-8'
    laparams = LAParams()
    rsrcmgr = PDFResourceManager()

    outfp = StringIO()
    device = TextConverter(
        rsrcmgr, outfp, codec=codec, laparams=laparams)

    interpreter = PDFPageInterpreter(rsrcmgr, device)

    try:
        pagenos = set()
        for page in PDFPage.get_pages(
                fp,
                pagenos,
                maxpages=0,
                password='',
                caching=True,
                check_extractable=True):
            interpreter.process_page(page)
        fp.close()
    except:
        print 'Unable to process the PDF file'
        print content

    device.close()

    print '------------------'
    outfp.seek(0)
    print outfp.read()

    outfp.close()
