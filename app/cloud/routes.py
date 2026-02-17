from datetime import datetime, timezone

from flask import (
    render_template, redirect, url_for, flash, request, jsonify,
)
from flask_login import login_required, current_user

from app.cloud import cloud_bp
from app.cloud.forms import AWSConnectionForm, AzureConnectionForm
from app.extensions import db
from app.models.cloud_connection import CloudConnection
from app.models.cached_resource import CachedResource
from app.utils.audit import log_action
from app.utils.decorators import admin_required


@cloud_bp.route('/connections')
@login_required
def list_connections():
    # Show user's own connections plus server defaults
    own = CloudConnection.query.filter_by(
        user_id=current_user.id, is_active=True
    ).all()
    defaults = CloudConnection.query.filter_by(
        user_id=None, is_default=True, is_active=True
    ).all()
    return render_template(
        'cloud/connections.html', own_connections=own, default_connections=defaults
    )


@cloud_bp.route('/connections/new/<provider>', methods=['GET', 'POST'])
@login_required
def create_connection(provider):
    if provider == 'aws':
        form = AWSConnectionForm()
    elif provider == 'azure':
        form = AzureConnectionForm()
    else:
        flash('Invalid provider.', 'danger')
        return redirect(url_for('cloud.list_connections'))

    # Only admins can create server-wide defaults
    if not current_user.is_admin and hasattr(form, 'is_default'):
        form.is_default.data = False

    if form.validate_on_submit():
        conn = CloudConnection(
            name=form.name.data,
            provider=provider,
            is_default=form.is_default.data if current_user.is_admin else False,
        )

        # Server default has no user_id; personal connection has user_id
        if conn.is_default:
            conn.user_id = None
        else:
            conn.user_id = current_user.id

        if provider == 'aws':
            conn.region = form.aws_default_region.data
            conn.set_credentials({
                'aws_access_key_id': form.aws_access_key_id.data,
                'aws_secret_access_key': form.aws_secret_access_key.data,
                'aws_default_region': form.aws_default_region.data,
            })
        elif provider == 'azure':
            conn.set_credentials({
                'tenant_id': form.tenant_id.data,
                'client_id': form.client_id.data,
                'client_secret': form.client_secret.data,
                'subscription_id': form.subscription_id.data,
            })

        db.session.add(conn)
        db.session.commit()
        log_action('create_connection', target_type='cloud_connection', target_id=conn.id)
        flash(f'{provider.upper()} connection "{conn.name}" created.', 'success')
        return redirect(url_for('cloud.list_connections'))

    return render_template(
        'cloud/connection_form.html', form=form, provider=provider, editing=False
    )


@cloud_bp.route('/connections/<uuid:conn_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_connection(conn_id):
    conn = _get_connection_or_404(conn_id)

    if conn.provider == 'aws':
        form = AWSConnectionForm(obj=conn)
    else:
        form = AzureConnectionForm(obj=conn)

    if form.validate_on_submit():
        conn.name = form.name.data
        if current_user.is_admin:
            conn.is_default = form.is_default.data
            conn.user_id = None if conn.is_default else current_user.id

        if conn.provider == 'aws':
            conn.region = form.aws_default_region.data
            conn.set_credentials({
                'aws_access_key_id': form.aws_access_key_id.data,
                'aws_secret_access_key': form.aws_secret_access_key.data,
                'aws_default_region': form.aws_default_region.data,
            })
        else:
            conn.set_credentials({
                'tenant_id': form.tenant_id.data,
                'client_id': form.client_id.data,
                'client_secret': form.client_secret.data,
                'subscription_id': form.subscription_id.data,
            })

        db.session.commit()
        log_action('edit_connection', target_type='cloud_connection', target_id=conn.id)
        flash(f'Connection "{conn.name}" updated.', 'success')
        return redirect(url_for('cloud.list_connections'))

    return render_template(
        'cloud/connection_form.html', form=form, provider=conn.provider,
        editing=True, conn=conn
    )


@cloud_bp.route('/connections/<uuid:conn_id>/delete', methods=['POST'])
@login_required
def delete_connection(conn_id):
    conn = _get_connection_or_404(conn_id)
    conn.is_active = False
    db.session.commit()
    log_action('delete_connection', target_type='cloud_connection', target_id=conn.id)
    flash(f'Connection "{conn.name}" removed.', 'success')
    return redirect(url_for('cloud.list_connections'))


@cloud_bp.route('/connections/<uuid:conn_id>/test', methods=['POST'])
@login_required
def test_connection(conn_id):
    conn = _get_connection_or_404(conn_id)
    creds = conn.get_credentials()

    from app.utils.cli_runner import test_aws_connection, test_azure_connection

    if conn.provider == 'aws':
        success, result = test_aws_connection(creds)
    else:
        success, result = test_azure_connection(creds)

    if success:
        conn.last_tested = datetime.now(timezone.utc)
        db.session.commit()
        log_action('test_connection_success', target_type='cloud_connection', target_id=conn.id)
        return jsonify({'status': 'ok', 'message': 'Connection successful', 'details': result})
    else:
        log_action('test_connection_failed', target_type='cloud_connection', target_id=conn.id,
                   details={'error': str(result)[:500]})
        return jsonify({'status': 'error', 'message': str(result)}), 400


@cloud_bp.route('/resources')
@login_required
def list_resources():
    connection_id = request.args.get('connection_id')
    resource_type = request.args.get('resource_type')
    provider = request.args.get('provider')

    # Get connections visible to user
    visible_ids = _get_visible_connection_ids()

    query = CachedResource.query.filter(
        CachedResource.connection_id.in_(visible_ids)
    )

    if connection_id:
        query = query.filter_by(connection_id=connection_id)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)

    # Filter by provider via join
    if provider:
        query = query.join(CloudConnection).filter(CloudConnection.provider == provider)

    resources = query.order_by(CachedResource.resource_type, CachedResource.resource_name).all()

    # Get unique resource types for filter dropdown
    type_counts = db.session.query(
        CachedResource.resource_type, db.func.count(CachedResource.id)
    ).filter(
        CachedResource.connection_id.in_(visible_ids)
    ).group_by(CachedResource.resource_type).all()

    # Get connections for filter dropdown
    connections = CloudConnection.query.filter(
        CloudConnection.id.in_(visible_ids)
    ).all()

    return render_template(
        'cloud/resources.html',
        resources=resources,
        type_counts=type_counts,
        connections=connections,
        selected_connection=connection_id,
        selected_type=resource_type,
        selected_provider=provider,
    )


@cloud_bp.route('/resources/discover', methods=['POST'])
@login_required
def discover_resources():
    connection_id = request.json.get('connection_id') if request.is_json else request.form.get('connection_id')

    if not connection_id:
        return jsonify({'status': 'error', 'message': 'No connection specified'}), 400

    conn = _get_connection_or_404(connection_id)

    from app.cloud.discovery import run_discovery
    try:
        count = run_discovery(conn)
        log_action('discover_resources', target_type='cloud_connection', target_id=conn.id,
                   details={'resources_found': count})
        return jsonify({'status': 'ok', 'message': f'Discovered {count} resources', 'count': count})
    except Exception as e:
        log_action('discover_resources_failed', target_type='cloud_connection', target_id=conn.id,
                   details={'error': str(e)[:500]})
        return jsonify({'status': 'error', 'message': str(e)}), 500


@cloud_bp.route('/resources/<uuid:resource_id>')
@login_required
def resource_detail(resource_id):
    resource = db.session.get(CachedResource, resource_id)
    if resource is None:
        flash('Resource not found.', 'danger')
        return redirect(url_for('cloud.list_resources'))

    visible_ids = _get_visible_connection_ids()
    if resource.connection_id not in visible_ids:
        flash('Access denied.', 'danger')
        return redirect(url_for('cloud.list_resources'))

    return render_template('cloud/resource_detail.html', resource=resource)


def get_effective_connection(user, provider):
    user_conn = CloudConnection.query.filter_by(
        user_id=user.id, provider=provider, is_active=True
    ).first()
    if user_conn:
        return user_conn
    return CloudConnection.query.filter_by(
        user_id=None, provider=provider, is_default=True, is_active=True
    ).first()


def _get_visible_connection_ids():
    own = CloudConnection.query.filter_by(
        user_id=current_user.id, is_active=True
    ).with_entities(CloudConnection.id).all()
    defaults = CloudConnection.query.filter_by(
        user_id=None, is_default=True, is_active=True
    ).with_entities(CloudConnection.id).all()
    return [c.id for c in own + defaults]


def _get_connection_or_404(conn_id):
    from flask import abort
    conn = db.session.get(CloudConnection, conn_id)
    if conn is None or not conn.is_active:
        abort(404)
    # User can access their own connections and server defaults
    if conn.user_id is not None and conn.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return conn
