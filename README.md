# 1. Initialize your database schema
python manage.py makemigrations
python manage.py migrate

# 2. Create a superuser so you can log in to the admin
python manage.py createsuperuser

# 3. (Optional) Collect static assets for production
python manage.py collectstatic

# 4. Start the development server
python manage.py runserver
