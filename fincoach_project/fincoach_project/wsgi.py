"""
WSGI entry point — used when deploying to a real web server.
You won't need to touch this during development.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincoach_project.settings")
application = get_wsgi_application()
