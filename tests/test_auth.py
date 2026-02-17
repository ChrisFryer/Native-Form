def test_login_page_loads(client):
    resp = client.get('/auth/login')
    assert resp.status_code == 200
    assert b'Sign In' in resp.data


def test_register_page_loads(client):
    resp = client.get('/auth/register')
    assert resp.status_code == 200
    assert b'Register' in resp.data


def test_register_and_login(client, db):
    # Register
    resp = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123',
        'password_confirm': 'securepassword123',
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Login
    resp = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'securepassword123',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data


def test_login_invalid_credentials(client, db):
    resp = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    assert b'Invalid username or password' in resp.data


def test_logout(client, db):
    # Register + login first
    client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword123',
        'password_confirm': 'securepassword123',
    })
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'securepassword123',
    })

    resp = client.get('/auth/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'logged out' in resp.data


def test_first_user_is_admin(client, db):
    from app.models.user import User
    client.post('/auth/register', data={
        'username': 'firstadmin',
        'email': 'admin@example.com',
        'password': 'securepassword123',
        'password_confirm': 'securepassword123',
    })
    user = User.query.filter_by(username='firstadmin').first()
    assert user is not None
    assert user.role == 'admin'


def test_dashboard_requires_login(client):
    resp = client.get('/dashboard')
    assert resp.status_code == 302
