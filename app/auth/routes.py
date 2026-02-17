from datetime import datetime, timezone

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.extensions import db
from app.models.user import User
from app.utils.audit import log_action


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Local authentication
        if user and user.is_active and user.auth_method == 'local':
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                log_action('login')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))

        # LDAP authentication (if enabled)
        from flask import current_app
        if current_app.config.get('LDAP_ENABLED'):
            from app.auth.ldap_auth import try_ldap_login, sync_ldap_user
            ldap_result = try_ldap_login(
                form.username.data, form.password.data
            )
            if ldap_result:
                user = sync_ldap_user(ldap_result)
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                log_action('login_ldap')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='viewer',
            auth_method='local',
        )
        user.set_password(form.password.data)

        # First registered user becomes admin
        if User.query.count() == 0:
            user.role = 'admin'

        db.session.add(user)
        db.session.commit()
        log_action('register', target_type='user', target_id=user.id)
        flash('Registration successful. Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    log_action('logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.auth_method != 'local':
        flash('Password changes are managed by your LDAP administrator.', 'warning')
        return redirect(url_for('main.dashboard'))

    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_action('change_password')
            flash('Password updated successfully.', 'success')
            return redirect(url_for('main.dashboard'))

    return render_template('auth/change_password.html', form=form)
