import csv
import io
import json

from flask import request, Response, jsonify
from flask_login import login_required, current_user

from app.export import export_bp
from app.extensions import db
from app.models.cached_resource import CachedResource
from app.models.cloud_connection import CloudConnection
from app.utils.audit import log_action


@export_bp.route('/csv')
@login_required
def export_csv():
    resources = _get_filtered_resources()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        'Resource Type', 'Resource ID', 'Name', 'Region',
        'Connection', 'Provider', 'Discovered At',
    ])
    for r in resources:
        writer.writerow([
            r.resource_type,
            r.resource_id,
            r.resource_name or '',
            r.region or '',
            r.connection.name,
            r.connection.provider,
            r.discovered_at.isoformat(),
        ])

    log_action('export_csv', details={'count': len(resources)})

    return Response(
        si.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=native-form-resources.csv'},
    )


@export_bp.route('/json')
@login_required
def export_json():
    resource_id = request.args.get('resource_id')

    if resource_id:
        resource = db.session.get(CachedResource, resource_id)
        if resource is None:
            return jsonify({'error': 'Resource not found'}), 404
        data = {
            'resource_type': resource.resource_type,
            'resource_id': resource.resource_id,
            'resource_name': resource.resource_name,
            'region': resource.region,
            'discovered_at': resource.discovered_at.isoformat(),
            'raw_data': resource.raw_data,
        }
        log_action('export_json', details={'resource_id': resource_id})
    else:
        resources = _get_filtered_resources()
        data = []
        for r in resources:
            data.append({
                'resource_type': r.resource_type,
                'resource_id': r.resource_id,
                'resource_name': r.resource_name,
                'region': r.region,
                'connection': r.connection.name,
                'provider': r.connection.provider,
                'discovered_at': r.discovered_at.isoformat(),
                'raw_data': r.raw_data,
            })
        log_action('export_json', details={'count': len(data)})

    output = json.dumps(data, indent=2, default=str)
    return Response(
        output,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=native-form-resources.json'},
    )


def _get_filtered_resources():
    connection_id = request.args.get('connection_id')
    resource_type = request.args.get('resource_type')

    # Only export resources the user can see
    visible_ids = _get_visible_connection_ids()

    query = CachedResource.query.filter(
        CachedResource.connection_id.in_(visible_ids)
    )
    if connection_id:
        query = query.filter_by(connection_id=connection_id)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)

    return query.all()


def _get_visible_connection_ids():
    own = CloudConnection.query.filter_by(
        user_id=current_user.id, is_active=True
    ).with_entities(CloudConnection.id).all()
    defaults = CloudConnection.query.filter_by(
        user_id=None, is_default=True, is_active=True
    ).with_entities(CloudConnection.id).all()
    return [c.id for c in own + defaults]
