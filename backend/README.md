python -m venv dj

dj\Scripts\activate

pip install pipenv djangorestframework

pipenv install django django-debug-toolbar

pipenv shell

django-admin startproject back

cd back

python manage.py runserver

python manage.py startapp api

python manage.py makemigrations api

python manage.py migrate
