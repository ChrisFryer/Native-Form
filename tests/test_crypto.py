from app.utils.crypto import encrypt_credentials, decrypt_credentials, encrypt_value, decrypt_value


def test_encrypt_decrypt_credentials(app):
    with app.app_context():
        original = {
            'aws_access_key_id': 'AKIAIOSFODNN7EXAMPLE',
            'aws_secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        }
        encrypted = encrypt_credentials(original)
        assert encrypted != str(original)
        assert 'AKIAIOSFODNN7EXAMPLE' not in encrypted

        decrypted = decrypt_credentials(encrypted)
        assert decrypted == original


def test_encrypt_decrypt_value(app):
    with app.app_context():
        original = 'sensitive-password-123'
        encrypted = encrypt_value(original)
        assert encrypted != original
        decrypted = decrypt_value(encrypted)
        assert decrypted == original
