from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.admin import admin_bp
from app.admin.forms import (
    EditUserForm, SystemSettingsForm, DefaultAWSForm, DefaultAzureForm,
)
from app.extensions import db
from app.models.user import User
from app.models.cloud_connection import CloudConnection
from app.models.audit_log import AuditLog
from app.models.system_setting import SystemSetting
from app.utils.decorators import admin_required
from app.utils.audit import log_action


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<uuid:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.list_users'))

    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.role = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        log_action('edit_user', target_type='user', target_id=user.id,
                   details={'role': user.role, 'is_active': user.is_active})
        flash(f'User "{user.username}" updated.', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/edit_user.html', form=form, user=user)


@admin_bp.route('/users/<uuid:user_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash('User not found.', 'danger')
    else:
        user.is_active = False
        db.session.commit()
        log_action('deactivate_user', target_type='user', target_id=user.id)
        flash(f'User "{user.username}" deactivated.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    form = SystemSettingsForm()

    if request.method == 'GET':
        form.registration_enabled.data = SystemSetting.get('registration_enabled', 'true') == 'true'
        form.ldap_enabled.data = SystemSetting.get('ldap_enabled', 'false') == 'true'
        form.ldap_host.data = SystemSetting.get('ldap_host', '')
        form.ldap_port.data = int(SystemSetting.get('ldap_port', '389'))
        form.ldap_use_ssl.data = SystemSetting.get('ldap_use_ssl', 'false') == 'true'
        form.ldap_base_dn.data = SystemSetting.get('ldap_base_dn', '')
        form.ldap_user_dn.data = SystemSetting.get('ldap_user_dn', '')
        form.ldap_user_login_attr.data = SystemSetting.get('ldap_user_login_attr', 'sAMAccountName')
        form.ldap_bind_user_dn.data = SystemSetting.get('ldap_bind_user_dn', '')

    if form.validate_on_submit():
        SystemSetting.set('registration_enabled', str(form.registration_enabled.data).lower())
        SystemSetting.set('ldap_enabled', str(form.ldap_enabled.data).lower())
        SystemSetting.set('ldap_host', form.ldap_host.data or '')
        SystemSetting.set('ldap_port', str(form.ldap_port.data or 389))
        SystemSetting.set('ldap_use_ssl', str(form.ldap_use_ssl.data).lower())
        SystemSetting.set('ldap_base_dn', form.ldap_base_dn.data or '')
        SystemSetting.set('ldap_user_dn', form.ldap_user_dn.data or '')
        SystemSetting.set('ldap_user_login_attr', form.ldap_user_login_attr.data or 'sAMAccountName')
        SystemSetting.set('ldap_bind_user_dn', form.ldap_bind_user_dn.data or '')
        if form.ldap_bind_user_password.data:
            SystemSetting.set('ldap_bind_user_password', form.ldap_bind_user_password.data, encrypted=True)

        log_action('update_settings')
        flash('Settings saved.', 'success')
        return redirect(url_for('admin.system_settings'))

    return render_template('admin/settings.html', form=form)


@admin_bp.route('/audit-log')
@login_required
@admin_required
def audit_log_view():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    pagination = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/audit_log.html', pagination=pagination)


@admin_bp.route('/defaults/aws', methods=['GET', 'POST'])
@login_required
@admin_required
def default_aws():
    existing = CloudConnection.query.filter_by(
        user_id=None, provider='aws', is_default=True, is_active=True
    ).first()

    form = DefaultAWSForm()
    if request.method == 'GET' and existing:
        form.name.data = existing.name
        form.aws_default_region.data = existing.region

    if form.validate_on_submit():
        if existing is None:
            existing = CloudConnection(
                provider='aws', is_default=True, user_id=None
            )
            db.session.add(existing)

        existing.name = form.name.data
        existing.region = form.aws_default_region.data
        existing.set_credentials({
            'aws_access_key_id': form.aws_access_key_id.data,
            'aws_secret_access_key': form.aws_secret_access_key.data,
            'aws_default_region': form.aws_default_region.data,
        })
        db.session.commit()
        log_action('update_default_aws', target_type='cloud_connection', target_id=existing.id)
        flash('Default AWS credentials saved.', 'success')
        return redirect(url_for('admin.system_settings'))

    return render_template('admin/default_cloud.html', form=form, provider='aws', existing=existing)


@admin_bp.route('/defaults/azure', methods=['GET', 'POST'])
@login_required
@admin_required
def default_azure():
    existing = CloudConnection.query.filter_by(
        user_id=None, provider='azure', is_default=True, is_active=True
    ).first()

    form = DefaultAzureForm()
    if request.method == 'GET' and existing:
        form.name.data = existing.name

    if form.validate_on_submit():
        if existing is None:
            existing = CloudConnection(
                provider='azure', is_default=True, user_id=None
            )
            db.session.add(existing)

        existing.name = form.name.data
        existing.set_credentials({
            'tenant_id': form.tenant_id.data,
            'client_id': form.client_id.data,
            'client_secret': form.client_secret.data,
            'subscription_id': form.subscription_id.data,
        })
        db.session.commit()
        log_action('update_default_azure', target_type='cloud_connection', target_id=existing.id)
        flash('Default Azure credentials saved.', 'success')
        return redirect(url_for('admin.system_settings'))

    return render_template('admin/default_cloud.html', form=form, provider='azure', existing=existing)
