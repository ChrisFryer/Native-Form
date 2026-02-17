import json
import os
import subprocess

from flask import current_app


class CLIError(Exception):
    def __init__(self, command, returncode, stderr):
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"CLI command failed (rc={returncode}): {stderr[:500]}")


def run_aws_command(args, credentials, timeout=None):
    if timeout is None:
        timeout = current_app.config['DISCOVERY_TIMEOUT_SECONDS']

    aws_path = current_app.config['AWS_CLI_PATH']
    cmd = [aws_path] + args + ['--output', 'json']

    env = _clean_env()
    env['AWS_ACCESS_KEY_ID'] = credentials['aws_access_key_id']
    env['AWS_SECRET_ACCESS_KEY'] = credentials['aws_secret_access_key']
    env['AWS_DEFAULT_REGION'] = credentials.get('aws_default_region', 'us-east-1')
    env['AWS_SHARED_CREDENTIALS_FILE'] = '/dev/null'
    env['AWS_CONFIG_FILE'] = '/dev/null'

    return _execute(cmd, env, timeout)


def run_azure_command(args, credentials, timeout=None):
    if timeout is None:
        timeout = current_app.config['DISCOVERY_TIMEOUT_SECONDS']

    az_path = current_app.config['AZ_CLI_PATH']
    env = _clean_env()
    env['AZURE_CLIENT_ID'] = credentials['client_id']
    env['AZURE_CLIENT_SECRET'] = credentials['client_secret']
    env['AZURE_TENANT_ID'] = credentials['tenant_id']

    cmd = [az_path] + args + [
        '--subscription', credentials['subscription_id'],
        '--output', 'json',
    ]

    return _execute(cmd, env, timeout)


def test_aws_connection(credentials):
    try:
        result = run_aws_command(['sts', 'get-caller-identity'], credentials, timeout=30)
        return True, result
    except CLIError as e:
        return False, str(e)


def test_azure_connection(credentials):
    try:
        result = run_azure_command(['account', 'show'], credentials, timeout=30)
        return True, result
    except CLIError as e:
        return False, str(e)


def _clean_env():
    safe_keys = ['PATH', 'HOME', 'LANG', 'LC_ALL', 'TERM', 'SYSTEMROOT', 'COMSPEC']
    return {k: v for k, v in os.environ.items() if k in safe_keys}


def _execute(cmd, env, timeout):
    for arg in cmd:
        if not isinstance(arg, str):
            raise ValueError(f"Command argument must be a string, got {type(arg)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        raise CLIError(cmd[0], -1, f"Command timed out after {timeout} seconds")
    except FileNotFoundError:
        raise CLIError(cmd[0], -1, f"CLI executable not found: {cmd[0]}")

    if result.returncode != 0:
        raise CLIError(cmd[0], result.returncode, result.stderr)

    if not result.stdout.strip():
        return {}

    return json.loads(result.stdout)
