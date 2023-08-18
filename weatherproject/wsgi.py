import os
from django.core.wsgi import get_wsgi_application

# Set the DJANGO_SETTINGS_MODULE environment variable to the correct path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weatherproject.settings")

application = get_wsgi_application()
app = application
