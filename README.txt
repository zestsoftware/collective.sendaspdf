Introduction
============

collective.sendaspdf is an open source product for Plone that
allows downloading the page seen by the user as a PDF file. It also
provide a form to send the page by e-mail (a screenshot of the current
page in a PDF format being joined to the e-mail).

It relies on two products to generate the PDF files:

 - xhtml2pdf: http://www.xhtml2pdf.com/

 - wkhtmltopdf: http://code.google.com/p/wkhtmltopdf/

The site manager can easily chose which solution he prefers for
the generation.

Installing
==========

To install the package, you can simply add 'collective.sendaspdf'
to the eggs list in your buildout.
Then install it using Zope's quick installer or Plone's add-on
products manager.

To install xhtml2pdf, add the following to your buildout eggs
directory::

     pisa
     pyPdf
     html5lib
     reportlab

collective.sendaspdf has been tested with development versions of
pisa and html5lib. With the latest releases (when writing this
README - html5lib 0.9 and pisa 3.0.33) some pages could not be
rendered.

To install wkhtmltopdf, go to the projects page and download an
executable version for your OS. Install it so the command
'wkhtmltopdf' is in the PATH.
You can also update your buildout to automatically download 
wkhtmltopdf and have it used by your instance using the following
recipes::

  [buildout]
  parts =
      ...
      wkhtmltopdf
      wkhtmltopdf_executable

  [instance]
  ...
  environment-vars =
      ...
      WKHTMLTOPDF_PATH ${wkhtmltopdf:location}/wkhtmltopdf

  [wkhtmltopdf]
  recipe = hexagonit.recipe.download
  url = http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.9.9-static-amd64.tar.bz2

  [wkhtmltopdf_executable]
  recipe = collective.recipe.cmd
  on_install = true
  on_update = true
  cmds =
       cd ${buildout:directory}/parts/wkhtmltopdf
       mv wkhtmltopdf-amd64 wkhtmltopdf
       chmod +x wkhtmltopdf

You might have some changes to do depending on the architecture you
are using (this example is for the amd64 architecture)

Configuring
===========

Go to the Plone control panel. You will find a 'Send as PDF' link that
sends you to the products configuration page.

This page proposes a few settings:

 - the tool used to render the PDF files.

 - the directory where the PDF files are stored.

 - the sentence used as salt when hashing the user's emails
   (this hash is used to know which files a user can access)

 - the name used in the mail for the PDF file.

 - a default title/body for the mails.

For wkhtmltopdf user, two extra options are available:

 - always use the print CSS to render the PDF.

 - use the print CSS for a given set of objects.

xhtml2pdf always use the print CSS.
