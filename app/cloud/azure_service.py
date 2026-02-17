from app.utils.cli_runner import run_azure_command


def discover_virtual_machines(credentials):
    data = run_azure_command(['vm', 'list'], credentials)
    resources = []
    if isinstance(data, list):
        for vm in data:
            resources.append({
                'resource_type': 'azure_vm',
                'resource_id': vm.get('id', vm.get('name', '')),
                'resource_name': vm.get('name', ''),
                'region': vm.get('location', ''),
                'raw_data': vm,
            })
    return resources


def discover_storage_accounts(credentials):
    data = run_azure_command(['storage', 'account', 'list'], credentials)
    resources = []
    if isinstance(data, list):
        for sa in data:
            resources.append({
                'resource_type': 'azure_storage_account',
                'resource_id': sa.get('id', sa.get('name', '')),
                'resource_name': sa.get('name', ''),
                'region': sa.get('location', ''),
                'raw_data': sa,
            })
    return resources


def discover_sql_servers(credentials):
    data = run_azure_command(['sql', 'server', 'list'], credentials)
    resources = []
    if isinstance(data, list):
        for srv in data:
            resources.append({
                'resource_type': 'azure_sql_server',
                'resource_id': srv.get('id', srv.get('name', '')),
                'resource_name': srv.get('name', ''),
                'region': srv.get('location', ''),
                'raw_data': srv,
            })
    return resources


def discover_function_apps(credentials):
    data = run_azure_command(['functionapp', 'list'], credentials)
    resources = []
    if isinstance(data, list):
        for fa in data:
            resources.append({
                'resource_type': 'azure_function_app',
                'resource_id': fa.get('id', fa.get('name', '')),
                'resource_name': fa.get('name', ''),
                'region': fa.get('location', ''),
                'raw_data': fa,
            })
    return resources


def discover_virtual_networks(credentials):
    data = run_azure_command(['network', 'vnet', 'list'], credentials)
    resources = []
    if isinstance(data, list):
        for vnet in data:
            resources.append({
                'resource_type': 'azure_vnet',
                'resource_id': vnet.get('id', vnet.get('name', '')),
                'resource_name': vnet.get('name', ''),
                'region': vnet.get('location', ''),
                'raw_data': vnet,
            })
    return resources


def discover_resource_groups(credentials):
    data = run_azure_command(['group', 'list'], credentials)
    resources = []
    if isinstance(data, list):
        for rg in data:
            resources.append({
                'resource_type': 'azure_resource_group',
                'resource_id': rg.get('id', rg.get('name', '')),
                'resource_name': rg.get('name', ''),
                'region': rg.get('location', ''),
                'raw_data': rg,
            })
    return resources


AZURE_DISCOVERY_FUNCTIONS = [
    discover_virtual_machines,
    discover_storage_accounts,
    discover_sql_servers,
    discover_function_apps,
    discover_virtual_networks,
    discover_resource_groups,
]
