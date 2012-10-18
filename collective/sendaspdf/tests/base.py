# -*- coding: utf-8 -*-

import unittest
import doctest

from Testing import ZopeTestCase as ztc

try:
    from Zope2.App import zcml
    is_plone_3 = False
except ImportError:
    # Plone 3
    is_plone_3 = True
    from Products.Five import  zcml

try:
    from Testing.testbrowser import Browser
except ImportError:
    # Plone 3
    from Products.Five.testbrowser import Browser

import transaction
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

from zope.component import getSiteManager
from Acquisition import aq_base
from Products.MailHost.interfaces import IMailHost


import collective.sendaspdf
from collective.sendaspdf.tests.sendaspdf_parser import SendAsPDFHtmlParser
from collective.sendaspdf.tests.utils import MockMailHost
from collective.sendaspdf.emailer import su

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

class SendAsPDFTestCase(ptc.FunctionalTestCase):
    is_plone_3 = is_plone_3

    # We'll use those pages taken from Wikipedia pages about Plone
    # to create some pages in the system.
    # We chose english for its lack of accentued characters, french
    # because it mixes normal and accentued characters and Japanese
    # for the use of non-latin characters.
    # (my apologies to Japanese people if I make the text sound weird
    # by cutting it at 80 characters, I don't really have a clue about
    # what the text means).
    data = {'en': """
            <p>Plone is a free and open source content management system
            built on top of the Zope application server. In principle,
            Plone can be used for any kind of website, including blogs,
            internet sites, webshops and internal websites. It is also well
            positioned to be used as a document publishing system and groupware
            collaboration tool. The strengths of Plone are its flexible and
            adaptable workflow, very good security, extensibility, high
            usability and flexibility.</p>
            <p>Plone is released under the GNU General Public License (GPL) and
            is designed to be extensible. Major development is conducted
            periodically during special meetings called Plone Sprints.
            Additional functionality is added to Plone with Products,
            which may be distributed through the Plone website or otherwise.
            The Plone Foundation holds and enforces all copyrights and trademarks.
            Plone also has legal backing from the council of the Software
            Freedom Law Center.</p>
            <p>MediaWiki's "Monobook" layout is based partially on the
            Plone style sheets. High-profile public sector users include
            the Federal Bureau of Investigation, Brazilian Government, United
            Nations, City of Bern (Switzerland), New South Wales Government
            (Australia), and European Environment Agency.""",

            'fr':  """
            <p>Plone est un système de gestion de contenu Web libre publié
            selon les termes de la GNU GPL. Il est construit au-dessus du
            serveur d'applications Zope et de son extension CMF
            (Content Management Framework).</p>
            <p>Plone est entièrement objet et modulaire. Il permet de
            créer et gérer les aspects d'un site web, comme les utilisateurs,
            les « workflows » ou les documents attachables.</p>
            <p>Le fait que Plone soit programmé sur Zope fait qu'il est
            moins utilisé que d'autres systèmes de gestion de contenu,
            Zope étant connu pour sa courbe d'apprentissage assez lente
            (le fameux ZopeZen). Toutefois, Plone est considéré comme étant
            l'un des meilleurs CMS open-source existants, et est utilisé entre
            autres par le site web de la FSF, la Fondation pour le logiciel
            libre.</p>
            """,

            'jp': """
            <p>PloneはZopeアプリケーションサーバ上に構築されたフリーかつオープンなコ
            ンテンツマネジメントシステムである。基本的にPloneは、ブログ、インターネットサイト
            、ウェブショップや組織内のWebサイトといったどのような用途にも利用できる。さらに文
            書管理システムやグループウェアといった共有ツールとしても利用できるようになっている
            。Ploneの強みは、その柔軟で適応性のあるワークフロー、非常に優れたセキュリティ、拡張性
            、高いユーザビリティと柔軟性である</p>
            <p>PloneはGNU General Public License(GPL)ライセンスでリリースされており
            、拡張し易いように設計されている。主な開発は、定期的に開催される Plone スプリン
            トと呼ばれる特別なミーティング(ハッカソン)で行われる。Ploneに対する追加機能はプ
            ロダクトで追加する。それはPloneのウェブサイトかその他のサイトで配布されている。
            Plone財団は全ての著作権と商標を保持している。さらにPloneはSoftware Freedom
            Law Centerの評議会からの法的な後ろ盾も持っている。</p>
            <p>MediaWikiの"Monobook [JP]"レイアウトは部分的にPloneのスタイルシートをベー
            スにしている。</p>
            """}

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        # his hack allows us to get the traceback when the getting a
        # 500 error when using the browser.
        self.portal.error_log._ignored_exceptions = ()
        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising
        transaction.commit()
        
    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def login_as_user(self, username, password):
        self.browser.open('http://nohost/plone/logout')
        self.browser.open('http://nohost/plone/login_form')
        self.browser.getControl(name='__ac_name').value = username
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()

    def login_as_manager(self):
        self.login_as_user(
            ptc.portal_owner,
            ptc.default_password)

    def install_products(self):
        self.browser = Browser()

        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml',
                         collective.sendaspdf)
        zcml.load_config('tests.zcml',
                         collective.sendaspdf)

        ztc.installPackage(collective.sendaspdf)
        self.addProfile('collective.sendaspdf:default')
        self.addProfile('collective.sendaspdf:tests')
        self.addProduct('collective.sendaspdf')

    def create_folder(self, parent, title):
        self.login_as_manager()
        self.browser.open('%s/createObject?type_name=Folder' % parent.absolute_url())
        self.browser.getControl(name='title').value = title
        self.browser.getControl(name='form.button.save').click()
        return self.browser.url

    def create_page(self, language, title = None, parent = None):
        self.login_as_manager()
        if parent is None:
            parent = self.portal

        self.browser.open('%s/createObject?type_name=Document' % parent.absolute_url())
        if title is None:
            title = 'Plone (%s)' % language

        self.browser.getControl(name='title').value = title
        self.browser.getControl(name='text').value = self.data.get(language, 'Oups ...')
        self.browser.getControl(name='form.button.save').click()
        return self.browser.url

    def create_image(self, img_file, img_file_type, parent = None):
        self.login_as_manager()
        if parent is None:
            parent = self.portal

        def mydir():
            import os.path, sys
            if __name__ == '__main__':
                filename = sys.argv[0]
            else:
                filename = __file__
            return os.path.abspath(os.path.dirname(filename))


        self.browser.open('%s/createObject?type_name=Image' % parent.absolute_url())
        file_control = self.browser.getControl(name='image_file')
        file_control.mech_control.add_file(file(mydir() +  '/' + img_file),
                                           img_file_type,
                                           img_file)
        self.browser.getControl(name='form.button.save').click()
        return self.browser.url


    def setup_data(self):
        self.install_products()
        for lang in self.data.keys():
            self.create_page(lang)

        # We also add a page for which the title will contain
        # non-ASCII characters.
        # Depending on Plone version, the generated ID is not the same, so we first
        # generate the page with a simple title for which id is safe, then we'll edit
        # the title.
        self.cyrilic_title_page_url = self.create_page(None, 'Cyrilic title page')
        self.browser.open('%s/edit' % self.cyrilic_title_page_url)
        self.browser.getControl(name='title').value = '3цдса'
        self.browser.getControl(name='form.button.save').click()

    def get_sendaspdf_actions(self):
        """ Finds the links generated by send as pdf in browser contents.
        """
        parser = SendAsPDFHtmlParser()
        parser.feed(self.browser.contents)
        return parser.get_document_actions()

    def list_available_controls(self, form_name, before = None, hidden=[]):
        """
        Before can be used to print something before the form
        That can be usefull for example when the first line printed
        start with a non-deterministic value as you can not
        use an ellipsis.
        """
        
        if before is not None:
            print before

        # Code from here: http://plone.org/documentation/manual/plone-community-developer-documentation/testing-and-debugging/functional-testing#listing-available-form-controls
        form = self.browser.getForm(name=form_name)
        # get and print all controls
        for ctrl in form.mech_form.controls:
            try:
                control = self.browser.getControl(name=ctrl.name)
                if control.name in hidden:
                    continue

                print "%s: %s (%s)" % (control.name,
                                       control.value,
                                       control.type)
                print control.controls
            except:
                pass
