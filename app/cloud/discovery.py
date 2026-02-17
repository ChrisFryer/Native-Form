from flask import current_app

from app.extensions import db
from app.models.cached_resource import CachedResource
from app.utils.cli_runner import CLIError


def run_discovery(connection):
    credentials = connection.get_credentials()

    if connection.provider == 'aws':
        from app.cloud.aws_service import AWS_DISCOVERY_FUNCTIONS
        discovery_functions = AWS_DISCOVERY_FUNCTIONS
    elif connection.provider == 'azure':
        from app.cloud.azure_service import AZURE_DISCOVERY_FUNCTIONS
        discovery_functions = AZURE_DISCOVERY_FUNCTIONS
    else:
        raise ValueError(f"Unknown provider: {connection.provider}")

    # Clear old cached resources for this connection
    CachedResource.query.filter_by(connection_id=connection.id).delete()

    total = 0
    errors = []

    for discover_fn in discovery_functions:
        try:
            resources = discover_fn(credentials)
            for res_data in resources:
                resource = CachedResource(
                    connection_id=connection.id,
                    resource_type=res_data['resource_type'],
                    resource_id=res_data['resource_id'],
                    resource_name=res_data.get('resource_name'),
                    region=res_data.get('region'),
                    raw_data=res_data['raw_data'],
                )
                db.session.add(resource)
                total += 1
        except CLIError as e:
            errors.append(f"{discover_fn.__name__}: {e}")
            current_app.logger.warning(
                f"Discovery error for {connection.name}: {discover_fn.__name__}: {e}"
            )

    db.session.commit()

    if errors and total == 0:
        raise RuntimeError(
            f"All discoveries failed. Errors: {'; '.join(errors)}"
        )

    return total
