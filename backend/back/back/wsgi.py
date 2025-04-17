"""
WSGI config for back project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# ADD THESE LINES AT THE TOP
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to /back
sys.path.extend([
    str(BASE_DIR),
    str(BASE_DIR.parent)  # /backend
])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
application = get_wsgi_application()