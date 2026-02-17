from app.utils.cli_runner import run_aws_command


def discover_ec2_instances(credentials):
    data = run_aws_command(['ec2', 'describe-instances'], credentials)
    resources = []
    for reservation in data.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            name = ''
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']
                    break
            resources.append({
                'resource_type': 'ec2_instance',
                'resource_id': instance['InstanceId'],
                'resource_name': name,
                'region': credentials.get('aws_default_region', 'us-east-1'),
                'raw_data': instance,
            })
    return resources


def discover_s3_buckets(credentials):
    data = run_aws_command(['s3api', 'list-buckets'], credentials)
    resources = []
    for bucket in data.get('Buckets', []):
        resources.append({
            'resource_type': 's3_bucket',
            'resource_id': bucket['Name'],
            'resource_name': bucket['Name'],
            'region': credentials.get('aws_default_region', 'us-east-1'),
            'raw_data': bucket,
        })
    return resources


def discover_rds_instances(credentials):
    data = run_aws_command(['rds', 'describe-db-instances'], credentials)
    resources = []
    for db_inst in data.get('DBInstances', []):
        resources.append({
            'resource_type': 'rds_instance',
            'resource_id': db_inst.get('DBInstanceArn', db_inst['DBInstanceIdentifier']),
            'resource_name': db_inst['DBInstanceIdentifier'],
            'region': credentials.get('aws_default_region', 'us-east-1'),
            'raw_data': db_inst,
        })
    return resources


def discover_lambda_functions(credentials):
    data = run_aws_command(['lambda', 'list-functions'], credentials)
    resources = []
    for func in data.get('Functions', []):
        resources.append({
            'resource_type': 'lambda_function',
            'resource_id': func.get('FunctionArn', func['FunctionName']),
            'resource_name': func['FunctionName'],
            'region': credentials.get('aws_default_region', 'us-east-1'),
            'raw_data': func,
        })
    return resources


def discover_iam_users(credentials):
    data = run_aws_command(['iam', 'list-users'], credentials)
    resources = []
    for user in data.get('Users', []):
        resources.append({
            'resource_type': 'iam_user',
            'resource_id': user.get('Arn', user['UserName']),
            'resource_name': user['UserName'],
            'region': 'global',
            'raw_data': user,
        })
    return resources


def discover_vpcs(credentials):
    data = run_aws_command(['ec2', 'describe-vpcs'], credentials)
    resources = []
    for vpc in data.get('Vpcs', []):
        name = ''
        for tag in vpc.get('Tags', []):
            if tag['Key'] == 'Name':
                name = tag['Value']
                break
        resources.append({
            'resource_type': 'vpc',
            'resource_id': vpc['VpcId'],
            'resource_name': name or vpc['VpcId'],
            'region': credentials.get('aws_default_region', 'us-east-1'),
            'raw_data': vpc,
        })
    return resources


AWS_DISCOVERY_FUNCTIONS = [
    discover_ec2_instances,
    discover_s3_buckets,
    discover_rds_instances,
    discover_lambda_functions,
    discover_iam_users,
    discover_vpcs,
]
