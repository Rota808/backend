## Configuração do Banco de Dados

Altere o arquivo `/backend/back/back/settings.py` para incluir as credenciais corretas do banco de dados PostgreSQL.

### Exemplo:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": 'pizza',
        "USER": 'postgres',
        "PASSWORD": '1234',
        "HOST": 'localhost',
        "PORT": '5432',
    }
}

### Esse é o atual, vinculado ao azure

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

## Execução do Projeto

Acesse o diretório `/backend/back/` e execute os seguintes comandos:

python manage.py makemigrations api  
python manage.py migrate  
python manage.py runserver
