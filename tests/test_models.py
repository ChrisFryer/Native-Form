from app.models.user import User
from app.models.cloud_connection import CloudConnection


def test_user_password(db):
    user = User(username='test', email='test@test.com')
    user.set_password('mypassword')
    assert user.check_password('mypassword')
    assert not user.check_password('wrongpassword')


def test_user_admin_property(db):
    admin = User(username='admin', email='a@test.com', role='admin')
    viewer = User(username='viewer', email='v@test.com', role='viewer')
    assert admin.is_admin
    assert not viewer.is_admin


def test_cloud_connection_credentials(app, db):
    with app.app_context():
        conn = CloudConnection(
            name='test-aws',
            provider='aws',
            credentials_encrypted='',
        )
        creds = {
            'aws_access_key_id': 'AKIATEST123',
            'aws_secret_access_key': 'secretkey123',
            'aws_default_region': 'us-east-1',
        }
        conn.set_credentials(creds)
        assert conn.credentials_encrypted != ''

        decrypted = conn.get_credentials()
        assert decrypted['aws_access_key_id'] == 'AKIATEST123'
        assert decrypted['aws_secret_access_key'] == 'secretkey123'


def test_user_ldap_no_password(db):
    user = User(username='ldapuser', email='ldap@test.com', auth_method='ldap')
    assert not user.check_password('anything')
