import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('collective.sendaspdf')


def update_control_panel_and_tool(context):
    """Update our control panel action and tool.

    It may need a different icon expression (gif versus png).

    We first added it in the Plone category, but it should be in the
    Products category.

    For the tool: set the content icon properly, again gif versus png.

    For Plone 3, we do not touch the icons.  You might have a wrong
    icon then, but only when you install sendaspdf for the first time,
    which is more likely to happen on Plone 4.
    """
    controlPanel = getToolByName(context, 'portal_controlpanel')
    action = controlPanel.getActionObject('Plone/sendaspdf')
    if action is not None:
        action.category = 'Products'
        logger.info('Set sendaspdf controlpanel category to Products.')
    else:
        action = controlPanel.getActionObject('Products/sendaspdf')

    try:
        # Plone 4 or higher
        import plone.app.upgrade
        plone.app.upgrade  # pyflakes
        icon = 'string:${portal_url}/pdf_icon.png'
    except ImportError:
        # Plone 3
        # icon = 'string:${portal_url}/pdf_icon.gif'
        # Actually, we will do nothing anymore.
        return

    if action.icon_expr.text != icon:
        action.icon_expr.text = icon
        logger.info('Set sendaspdf controlpanel icon expression to %r', icon)

    # Now the tool.
    types = getToolByName(context, 'portal_types')
    typeinfo = types.getTypeInfo('SendAsPDFTool')
    if typeinfo is None:
        return
    if hasattr(typeinfo, 'icon_expr'):
        # Plone 4
        if typeinfo.icon_expr_object.text != icon:
            typeinfo.icon_expr_object.text = icon
            logger.info('Set sendaspdf tool icon expression to %r', icon)
