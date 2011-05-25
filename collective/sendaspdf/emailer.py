################################################################################
# Stollen from watcher list
# http://svn.plone.org/svn/collective/collective.watcherlist/trunk/collective/watcherlist/
################################################################################

import logging
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email import Encoders
from smtplib import SMTPException
import pkg_resources
import socket

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter

zope2_egg = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('Zope2'))
USE_SECURE_SEND = True
if zope2_egg and (zope2_egg.parsed_version >=
                  pkg_resources.parse_version('2.12.3')):
    USE_SECURE_SEND = False

logger = logging.getLogger('collective.sendaspdf')
DEFAULT_CHARSET = 'utf-8'

def get_charset():
    """Character set to use for encoding the email.

    If encoding fails we will try some other encodings.  We hope
    to get utf-8 here always actually.

    The getSiteEncoding call also works when portal is None, falling
    back to utf-8.  But that is only on Plone 4, not Plone 3.  So we
    handle that ourselves.
    """
    charset = None
    portal = getSite()
    if portal is None:
        return DEFAULT_CHARSET
    charset = portal.getProperty('email_charset', '')
    if not charset:
        charset = getSiteEncoding(portal)
    return charset

def su(value):
    """Return safe unicode version of value.
    """
    return safe_unicode(value, encoding=get_charset())

def get_mail_host():
    """Get the MailHost object.

    Return None in case of problems.
    """
    portal = getSite()
    if portal is None:
        return None
    request = portal.REQUEST
    ctrlOverview = getMultiAdapter((portal, request),
                                   name='overview-controlpanel')
    mail_settings_correct = not ctrlOverview.mailhost_warning()
    if mail_settings_correct:
        mail_host = getToolByName(portal, 'MailHost', None)
        return mail_host


def prepare_mail_message(msg, attachment, filename):
    """ Creates the message
    """
    html = msg

    # First, we transform the message in a text format.
    portal_transforms = getToolByName(getSite(),
                                      'portal_transforms')
    plain = portal_transforms.convert('html_to_text',
                                      html).getData()

    # We definitely want unicode at this point.
    plain = su(plain)
    html = su(html)

    # We must choose the body charset manually.  Note that the
    # goal and effect of this loop is to determine the
    # body_charset.
    for body_charset in 'US-ASCII', get_charset(), 'UTF-8':
        try:
            plain.encode(body_charset)
            html.encode(body_charset)
        except UnicodeEncodeError:
            pass
        else:
            break

    # Encoding should work now; let's replace errors just in case.
    plain = plain.encode(body_charset, 'replace')
    html = html.encode(body_charset, 'xmlcharrefreplace')

    text_part = MIMEText(plain, 'plain', body_charset)
    html_part = MIMEText(html, 'html', body_charset)

    # As we have plain text, html and attachment, we need to do
    # two multiparts:
    # - the first one contains the message
    # the second one includes the previous one and the attachment.
    email_content = MIMEMultipart('alternative')
    email_content.epilogue = ''
    email_content.attach(text_part)
    email_content.attach(html_part)

    # Now the attachment.
    attach = MIMEBase('application', 'pdf')
    attach.set_payload(attachment.read())
    Encoders.encode_base64(attach)
    attach.add_header('Content-Disposition',
                      'attachment; filename="%s"' % filename)

    # We attach everything to the mail.
    email_msg = MIMEMultipart()
    email_msg.attach(email_content)
    email_msg.attach(attach)
    return email_msg

def send_message(mfrom, mto, subject, message, attachment, filename):
    """ 
    """
    message = prepare_mail_message(message, attachment, filename)

    mail_host = get_mail_host()
    if mail_host is None:
        return

    mfrom = su(mfrom)
    mto = su(mto)
    subject = su(subject)
    header_charset = get_charset()

    try:
        if USE_SECURE_SEND:
            mail_host.secureSend(message=message,
                                 mto=mto,
                                 mfrom=mfrom,
                                 subject=subject,
                                 charset=header_charset)
        else:
           mail_host.send(message,
                          mto=mto,
                          mfrom=mfrom,
                          subject=subject,
                          immediate=True,
                          charset=header_charset)

    except (socket.error, SMTPException):
        logger.warn('Could not send email to %s with subject %s',
                    address, subject)
    except:
        raise
