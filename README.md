Em /backend/back/back/settings.py, altere as credenciais do banco

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": 'postgres',
        "USER": 'Antonio',
        "PASSWORD": 'a12345678@',
        "HOST": 'antonio.postgres.database.azure.com',
        "PORT": '5432',
    }
}

Para o mesmo estilo de:

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         "NAME": 'pizza',
#         "USER": 'postgres',
#         "PASSWORD": '1234',
#         "HOST": 'localhost',
#         "PORT": '5432',
#     }
# }

Em /backend/back/

python manage.py makemigrations api

python manage.py migrate

python manage.py runserver
