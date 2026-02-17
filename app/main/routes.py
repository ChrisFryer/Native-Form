from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.main import main_bp
from app.extensions import db
from app.models.cloud_connection import CloudConnection
from app.models.cached_resource import CachedResource
from app.models.audit_log import AuditLog


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Connections visible to user
    own_conns = CloudConnection.query.filter_by(
        user_id=current_user.id, is_active=True
    ).all()
    default_conns = CloudConnection.query.filter_by(
        user_id=None, is_default=True, is_active=True
    ).all()
    all_conns = own_conns + default_conns
    conn_ids = [c.id for c in all_conns]

    # Count by provider
    aws_count = sum(1 for c in all_conns if c.provider == 'aws')
    azure_count = sum(1 for c in all_conns if c.provider == 'azure')

    # Resource counts
    total_resources = 0
    resource_by_type = []
    if conn_ids:
        total_resources = CachedResource.query.filter(
            CachedResource.connection_id.in_(conn_ids)
        ).count()

        resource_by_type = db.session.query(
            CachedResource.resource_type, db.func.count(CachedResource.id)
        ).filter(
            CachedResource.connection_id.in_(conn_ids)
        ).group_by(CachedResource.resource_type).order_by(
            db.func.count(CachedResource.id).desc()
        ).all()

    # Recent audit entries
    recent_activity = AuditLog.query.filter_by(
        user_id=current_user.id
    ).order_by(AuditLog.created_at.desc()).limit(10).all()

    return render_template(
        'main/dashboard.html',
        aws_count=aws_count,
        azure_count=azure_count,
        total_connections=len(all_conns),
        total_resources=total_resources,
        resource_by_type=resource_by_type,
        recent_activity=recent_activity,
        connections=all_conns,
    )
