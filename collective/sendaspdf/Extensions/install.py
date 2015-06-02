""" Uninstall Profile
"""
from Products.CMFCore.utils import getToolByName


def uninstall(portal, reinstall=False):
    """ Uninstall profile setup
    """
    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')

        setup_tool.runAllImportStepsFromProfile(
            'profile-collective.sendaspdf:uninstall')

        portal.manage_delObjects(['portal_sendaspdf'])
        return "Ran all uninstall steps."
