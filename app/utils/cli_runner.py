import json
import os
import shutil
import subprocess
import tempfile

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

    # Azure CLI needs its own config dir for login state.
    # Use a temp directory so concurrent users don't conflict.
    az_config_dir = tempfile.mkdtemp(prefix='nf-az-')
    try:
        env = _clean_env()
        env['AZURE_CONFIG_DIR'] = az_config_dir

        # Azure CLI does not authenticate via env vars like AWS.
        # We must run 'az login --service-principal' first.
        login_cmd = [
            az_path, 'login', '--service-principal',
            '--username', credentials['client_id'],
            '--password', credentials['client_secret'],
            '--tenant', credentials['tenant_id'],
            '--output', 'none',
        ]
        _execute(login_cmd, env, timeout=30)

        # Now run the actual command
        cmd = [az_path] + args + [
            '--subscription', credentials['subscription_id'],
            '--output', 'json',
        ]
        return _execute(cmd, env, timeout)
    finally:
        shutil.rmtree(az_config_dir, ignore_errors=True)


def test_aws_connection(credentials):
    try:
        result = run_aws_command(['sts', 'get-caller-identity'], credentials, timeout=30)
        return True, result
    except CLIError as e:
        return False, str(e)


def test_azure_connection(credentials):
    try:
        result = run_azure_command(['account', 'show'], credentials, timeout=60)
        return True, result
    except CLIError as e:
        return False, str(e)


def _clean_env():
    """Build a restricted environment for CLI subprocesses.

    Strips application secrets but passes through system variables
    needed for CLI tools to function (Python paths, library paths, locale).
    """
    strip_keys = {
        'SECRET_KEY', 'FERNET_KEY', 'DATABASE_URL', 'FLASK_ENV',
        'SESSION_COOKIE_SECURE', 'LDAP_BIND_USER_PASSWORD',
        'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
        'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID',
    }
    return {k: v for k, v in os.environ.items() if k not in strip_keys}


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
