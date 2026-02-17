import ldap3
from flask import current_app

from app.extensions import db
from app.models.user import User


def try_ldap_login(username, password):
    config = current_app.config
    server = ldap3.Server(
        config['LDAP_HOST'],
        port=config['LDAP_PORT'],
        use_ssl=config['LDAP_USE_SSL'],
        get_info=ldap3.NONE,
    )

    user_dn = f"{config['LDAP_USER_RDN_ATTR']}={username},{config['LDAP_USER_DN']},{config['LDAP_BASE_DN']}"

    try:
        conn = ldap3.Connection(server, user=user_dn, password=password)
        if conn.bind():
            # Search for the user to get their email and display info
            search_base = f"{config['LDAP_USER_DN']},{config['LDAP_BASE_DN']}"
            search_filter = f"({config['LDAP_USER_LOGIN_ATTR']}={ldap3.utils.conv.escape_filter_chars(username)})"
            conn.search(
                search_base,
                search_filter,
                attributes=['mail', 'cn', 'sAMAccountName'],
            )
            if conn.entries:
                entry = conn.entries[0]
                return {
                    'username': username,
                    'email': str(entry.mail) if hasattr(entry, 'mail') else f'{username}@ldap.local',
                    'display_name': str(entry.cn) if hasattr(entry, 'cn') else username,
                }
            conn.unbind()
            return {'username': username, 'email': f'{username}@ldap.local'}
    except ldap3.core.exceptions.LDAPException:
        current_app.logger.warning(f'LDAP authentication failed for user: {username}')

    return None


def sync_ldap_user(ldap_result):
    user = User.query.filter_by(username=ldap_result['username']).first()
    if user is None:
        user = User(
            username=ldap_result['username'],
            email=ldap_result.get('email', f"{ldap_result['username']}@ldap.local"),
            auth_method='ldap',
            role='viewer',
        )
        db.session.add(user)
        db.session.commit()
    return user
