import os
import sys

# Ensure the project root is on the path so Django can find its modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myaiapp.settings")

from myaiapp.wsgi import application

# Vercel expects the WSGI callable to be named `app`
app = application
