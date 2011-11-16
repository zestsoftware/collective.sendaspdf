from collective.sendaspdf.browser.base import BaseView

class RealURLView(BaseView):
    """ We need this view to build the 'send as pdf'
    action menu.    
    """
    def __call__(self):
        base = self.context.REQUEST['ACTUAL_URL']
        method = self.context.REQUEST['REQUEST_METHOD']

        get_params = ''
        if method == 'GET':
            get_params = '&'.join(
                ['%s=%s' % (k, v) for k, v in self.context.REQUEST.form.items()
                 if k != '-C' and not (k == 'test' and v == '')])

        if get_params:
           base += '?' + get_params

        return base
