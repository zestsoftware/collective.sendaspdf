# Code taken from PDFMiner tool pdf2txt: https://github.com/euske/pdfminer/blob/master/tools/pdf2txt.py

import sys
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
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
