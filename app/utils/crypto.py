import json

from cryptography.fernet import Fernet
from flask import current_app


def _get_fernet():
    key = current_app.config['FERNET_KEY']
    if isinstance(key, str):
        key = key.encode('utf-8')
    return Fernet(key)


def encrypt_credentials(credentials_dict):
    f = _get_fernet()
    json_bytes = json.dumps(credentials_dict).encode('utf-8')
    return f.encrypt(json_bytes).decode('utf-8')


def decrypt_credentials(encrypted_str):
    f = _get_fernet()
    json_bytes = f.decrypt(encrypted_str.encode('utf-8'))
    return json.loads(json_bytes.decode('utf-8'))


def encrypt_value(plaintext):
    f = _get_fernet()
    return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')


def decrypt_value(encrypted_str):
    f = _get_fernet()
    return f.decrypt(encrypted_str.encode('utf-8')).decode('utf-8')


def generate_fernet_key():
    return Fernet.generate_key().decode('utf-8')
