import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FERNET_KEY = os.environ.get('FERNET_KEY')

    # Session security (set to True once TLS is configured)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # LDAP
    LDAP_ENABLED = os.environ.get('LDAP_ENABLED', 'false').lower() == 'true'
    LDAP_HOST = os.environ.get('LDAP_HOST', '')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', 389))
    LDAP_USE_SSL = os.environ.get('LDAP_USE_SSL', 'false').lower() == 'true'
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', '')
    LDAP_USER_DN = os.environ.get('LDAP_USER_DN', '')
    LDAP_GROUP_DN = os.environ.get('LDAP_GROUP_DN', '')
    LDAP_USER_RDN_ATTR = os.environ.get('LDAP_USER_RDN_ATTR', 'cn')
    LDAP_USER_LOGIN_ATTR = os.environ.get('LDAP_USER_LOGIN_ATTR', 'sAMAccountName')
    LDAP_BIND_USER_DN = os.environ.get('LDAP_BIND_USER_DN', '')
    LDAP_BIND_USER_PASSWORD = os.environ.get('LDAP_BIND_USER_PASSWORD', '')

    # CLI paths
    AWS_CLI_PATH = os.environ.get('AWS_CLI_PATH', '/usr/local/bin/aws')
    AZ_CLI_PATH = os.environ.get('AZ_CLI_PATH', '/usr/bin/az')

    # Discovery
    DISCOVERY_TIMEOUT_SECONDS = int(os.environ.get('DISCOVERY_TIMEOUT_SECONDS', 120))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    FERNET_KEY = 'dGVzdC1rZXktZm9yLXRlc3RpbmctMDEyMzQ1Njc4OQ=='
