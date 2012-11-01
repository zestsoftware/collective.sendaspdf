# Code taken from PDFMiner tool pdf2txt:
# https://github.com/euske/pdfminer/blob/master/tools/pdf2txt.py

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import process_pdf
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

    try:
        process_pdf(rsrcmgr, device, fp)
    except:
        print 'Unable to process the PDF file'
        print content

    device.close()

    print '------------------'
    outfp.seek(0)
    print outfp.read()

    outfp.close()
