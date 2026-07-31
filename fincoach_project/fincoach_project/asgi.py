"""
ASGI entry point — used for async deployment. Not needed during
development; kept here since it's part of Django's standard project
layout.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincoach_project.settings")
application = get_asgi_application()
