from collective.sendaspdf.browser.base import BaseView

class RealURLView(BaseView):
    """ We need this view to build the 'send as pdf'
    action menu.    
    """
    def __call__(self):
        base = self.context.REQUEST['ACTUAL_URL']
        get_params = '&'.join(
            ['%s=%s' % (k, v) for k, v in self.context.REQUEST.form.items()
             if k != '-C'])

        if get_params:
           base += '?' + get_params
        return base
