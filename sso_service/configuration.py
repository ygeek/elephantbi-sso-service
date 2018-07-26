import os
from datetime import timedelta

# Static Directory Settings
LOG_FILE_DIR = './local_data/logs/'


def get_db_uri(env='develop'):
    # Database
    if env == 'develop':
        username = os.getenv('DB_ENV_POSTGRES_USER_DEV')
        password = os.getenv('DB_ENV_POSTGRES_PASSWORD_DEV')
        host = os.getenv('DB_ENV_POSTGRES_HOST_DEV')
        port = os.getenv('DB_ENV_POSTGRES_PORT_DEV')
        database = os.getenv('DB_ENV_POSTGRES_DBNAME_DEV')

    elif env == 'stage':
        username = os.getenv('DB_ENV_POSTGRES_USER_STAGE')
        password = os.getenv('DB_ENV_POSTGRES_PASSWORD_STAGE')
        host = os.getenv('DB_ENV_POSTGRES_HOST_STAGE')
        port = os.getenv('DB_ENV_POSTGRES_PORT_STAGE')
        database = os.getenv('DB_ENV_POSTGRES_DBNAME_STAGE')

    else:
        username = os.getenv('DB_ENV_POSTGRES_USER_PROD')
        password = os.getenv('DB_ENV_POSTGRES_PASSWORD_PROD')
        host = os.getenv('DB_ENV_POSTGRES_HOST_PROD')
        port = os.getenv('DB_ENV_POSTGRES_PORT_PROD')
        database = os.getenv('DB_ENV_POSTGRES_DBNAME_PROD')

    # Flask-SQLAlchemy
    psql_conn_str_fmt = ('postgresql://'
                         '{username}:{password}@{host}:{port}/{database}')
    database_uri = psql_conn_str_fmt.format(
        username=username,
        password=password,
        host=host,
        port=port,
        database=database
    )

    return database_uri


class BaseConfig:
    # Builtin Configuration
    # SERVER_NAME = os.getenv('SERVER_NAME')

    # Flask-JWT
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_VERIFY_EXPIRATION = os.getenv('JWT_VERIFY_EXPIRATION', True)
    JWT_EXPIRATION_DELTA = timedelta(days=os.getenv('JWT_EXPIRATION_DELTA', 30))


class GeneralConfig(BaseConfig):
    # Server domain
    SERVER_DOMAIN = os.getenv('SERVER_DOMAIN')


class DevelopConfig(GeneralConfig):
    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = get_db_uri(env='develop')

    DEBUG = True


class StageConfig(GeneralConfig):
    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = get_db_uri(env='stage')

    DEBUG = False
    PROPAGATE_EXCEPTIONS = True


class ProductionConfig(GeneralConfig):
    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = get_db_uri(env='production')

    DEBUG = False
    PROPAGATE_EXCEPTIONS = True


def get_config(env='develop'):
    configs = {
        'develop': DevelopConfig,
        'stage': StageConfig,
        'production': ProductionConfig,
    }
    return configs[env]
