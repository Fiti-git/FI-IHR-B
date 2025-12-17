# myapi/middleware.py

from django.middleware.csrf import CsrfViewMiddleware

class ConditionalCsrfMiddleware(CsrfViewMiddleware):
    """
    This middleware conditionally applies CSRF protection.

    It will ONLY apply CSRF checks to paths that are NOT prefixed
    with '/myapi/'. All your API endpoints will be exempt.
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # If the path is for our API, skip CSRF protection entirely.
        if request.path.startswith('/myapi/'):
            return None

        # Otherwise, use the default CSRF protection.
        return super().process_view(request, callback, callback_args, callback_kwargs)