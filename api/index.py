import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Always force-set the correct settings module (strip any stray whitespace from env)
os.environ["DJANGO_SETTINGS_MODULE"] = "myaiapp.settings"

# Run migrations automatically on cold start (important for SQLite in /tmp on Vercel)
try:
    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", "--run-syncdb", verbosity=0)
except Exception:
    pass  # Don't crash the app if migration fails (e.g. no write access)

from myaiapp.wsgi import application

# Vercel expects the WSGI callable to be named `app`
app = application
