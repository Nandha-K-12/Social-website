from django.http import HttpResponseBadRequest

def ajax_required(f):
    def wrap(request, *args, **kwargs):
        # In Django 4.0+, request.headers.get('x-requested-with') is used
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or (
            hasattr(request, 'is_ajax') and request.is_ajax()
        )
        if not is_ajax:
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
