"""
WSGI config for ocr_poc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocr_poc.settings")

if 'DYNO' in os.environ:  # Running on Heroku
    from dj_static import Cling

    application = Cling(get_wsgi_application())
else:
    application = get_wsgi_application()
