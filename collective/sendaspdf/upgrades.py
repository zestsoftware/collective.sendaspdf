import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('collective.sendaspdf')


def update_control_panel(context):
    """Update our control panel action.

    It may need a different icon expression (gif versus png).

    We first added it in the Plone category, but it should be in the
    Products category.
    """
    try:
        # Plone 4 or higher
        import plone.app.upgrade
        plone.app.upgrade  # pyflakes
        icon = 'string:${portal_url}/pdf_icon.png'
    except ImportError:
        # Plone 3
        icon = 'string:${portal_url}/pdf_icon.gif'
    controlPanel = getToolByName(context, 'portal_controlpanel')
    action = controlPanel.getActionObject('Plone/sendaspdf')
    if action is not None:
        action.category = 'Products'
        logger.info('Set sendaspdf controlpanel category to Products.')
    else:
        action = controlPanel.getActionObject('Products/sendaspdf')
    if action.icon_expr.text != icon:
        action.icon_expr.text = icon
        logger.info('Set sendaspdf controlpanel icon expression to %r', icon)
