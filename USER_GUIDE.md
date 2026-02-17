# Native-Form User Guide

Native-Form is a cloud management application that queries AWS and Azure environments directly using native CLI commands, providing a real-time view of your cloud resources without maintaining a state file.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Cloud Connections](#cloud-connections)
4. [Resource Discovery](#resource-discovery)
5. [Resource Browser](#resource-browser)
6. [Exporting Data](#exporting-data)
7. [Administration](#administration)
8. [Security & Architecture](#security--architecture)

---

## Getting Started

### First-Time Login

1. Open your browser and navigate to `http://<your-server-ip>/`.
2. You will be redirected to the **Login** page.
3. Click **Register** to create your first account.
4. Fill in a username, email, and password (minimum 8 characters).
5. The **first registered user** is automatically assigned the **Admin** role.
6. After registering, sign in with your new credentials.

### User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access: manage users, system settings, server-wide default credentials, audit log, plus all viewer capabilities |
| **Viewer** | View dashboard, manage personal cloud connections, discover and browse resources, export data |

### Navigation

The top navigation bar provides access to all sections:

- **Dashboard** -- Overview of connections and resources
- **Connections** -- Manage cloud provider credentials
- **Resources** -- Browse and search discovered cloud resources
- **Export** -- Download resource data as CSV or JSON
- **Admin** (admin only) -- Users, Settings, Audit Log, Default Credentials
- **User menu** (top-right) -- Change password, logout

---

## Dashboard

The dashboard (`/dashboard`) displays:

- **Summary cards** -- Total connections, AWS accounts, Azure subscriptions, and discovered resources at a glance.
- **Resources by Type** -- A breakdown table showing how many of each resource type (EC2 instances, S3 buckets, VMs, etc.) have been discovered.
- **Connections** -- A list of all connections visible to you (personal and server defaults), with status indicators showing whether each has been tested.
- **Recent Activity** -- Your last 10 actions (logins, discoveries, exports, etc.) with timestamps.

---

## Cloud Connections

Cloud connections store the credentials needed to query AWS or Azure environments. Navigate to **Connections** in the navbar.

### Connection Types

- **Personal connections** -- Created by you, visible only to you. Any user can create personal connections.
- **Server-wide defaults** -- Created by admins, visible to all users. Used as a fallback when a user has no personal connection for a given provider.

**Credential hierarchy:** If you have a personal connection for a provider (e.g. AWS), it takes priority over the server-wide default for that provider.

### Adding an AWS Connection

1. Click **Add Connection** > **Amazon Web Services**.
2. Fill in the form:
   - **Connection Name** -- A friendly label (e.g. "Production AWS" or "Dev Account").
   - **AWS Access Key ID** -- Your IAM access key.
   - **AWS Secret Access Key** -- Your IAM secret key.
   - **Default Region** -- The AWS region to query (e.g. `us-east-1`, `ap-southeast-2`).
   - **Server Default** (admin only) -- Check this to make the connection available to all users.
3. Click **Save**.

### Adding an Azure Connection

1. Click **Add Connection** > **Microsoft Azure**.
2. Fill in the form:
   - **Connection Name** -- A friendly label (e.g. "Azure Production").
   - **Tenant ID** -- Your Azure AD tenant ID.
   - **Client ID** -- The application (service principal) client ID.
   - **Client Secret** -- The service principal secret.
   - **Subscription ID** -- The Azure subscription to query.
   - **Server Default** (admin only) -- Check this to make the connection available to all users.
3. Click **Save**.

### Testing a Connection

After creating a connection, click the **Test** button next to it. This runs:

- **AWS:** `aws sts get-caller-identity` to verify the access key is valid.
- **Azure:** `az account show` to verify the service principal can authenticate.

A green checkmark confirms the credentials are working. If the test fails, an error message will be displayed with details.

### Editing a Connection

Click the **pencil icon** next to any connection to update its name, credentials, or region. You must re-enter the secret key / client secret when editing (existing secrets are not displayed for security).

### Deleting a Connection

Click the **trash icon** next to a connection and confirm the prompt. This performs a soft delete (the connection is deactivated, not permanently removed from the database).

---

## Resource Discovery

Discovery scans your cloud environment using native CLI commands and caches the results in the database.

### Running a Discovery

1. Navigate to **Resources** in the navbar.
2. Click the **Discover** dropdown button (top-right).
3. Select the connection you want to scan.
4. A progress indicator appears while discovery runs.
5. When complete, the page refreshes to show the newly discovered resources.

### What Gets Discovered

**AWS Resources:**

| Resource Type | CLI Command Used |
|---------------|-----------------|
| EC2 Instances | `aws ec2 describe-instances` |
| S3 Buckets | `aws s3api list-buckets` |
| RDS Instances | `aws rds describe-db-instances` |
| Lambda Functions | `aws lambda list-functions` |
| IAM Users | `aws iam list-users` |
| VPCs | `aws ec2 describe-vpcs` |

**Azure Resources:**

| Resource Type | CLI Command Used |
|---------------|-----------------|
| Virtual Machines | `az vm list` |
| Storage Accounts | `az storage account list` |
| SQL Servers | `az sql server list` |
| Functions Apps | `az functionapp list` |
| Virtual Networks | `az network vnet list` |
| Resource Groups | `az group list` |

### How Discovery Works

- Each discovery run **replaces** the previously cached resources for that connection (old data is cleared before new results are stored).
- Credentials are decrypted in-memory only for the duration of the CLI call, then discarded.
- CLI commands are executed securely using argument lists (never shell execution), with credentials passed via environment variables.
- A configurable timeout (default 120 seconds) applies to each CLI command.

---

## Resource Browser

Navigate to **Resources** to view all discovered resources across your connections.

### Filtering

Use the filter bar at the top of the resource table to narrow results:

- **Provider** -- Show only AWS or Azure resources.
- **Resource Type** -- Filter by specific type (e.g. EC2 Instances, S3 Buckets). Each type shows a count of matching resources.
- **Connection** -- Filter by a specific cloud connection.
- **Clear** -- Reset all filters.

Filters auto-apply when changed (no need to click a submit button).

### Resource Detail View

Click the **Detail** button on any resource row to see:

- **Resource metadata** -- Type, ID (ARN or cloud ID), name, region, connection, and discovery timestamp.
- **Raw Data** -- The complete JSON response from the cloud CLI, formatted for readability. This contains every attribute the cloud provider returned for that resource.

### Exporting from the Resource Browser

The **Export** dropdown on the resource browser respects your current filters. If you've filtered to only EC2 instances from a specific connection, the export will contain only those matching resources.

---

## Exporting Data

Native-Form supports exporting discovered resources in two formats.

### CSV Export

Navigate to **Export** > **Export CSV** (from the navbar or the resource browser).

The CSV file includes these columns:
- Resource Type
- Resource ID (ARN or cloud ID)
- Name
- Region
- Connection name
- Provider
- Discovered At (timestamp)

### JSON Export

Navigate to **Export** > **Export JSON** (from the navbar or the resource browser).

The JSON export includes all CSV fields plus the complete **raw_data** object from the cloud CLI response, giving you the full detail for each resource.

### Single Resource Export

From the resource detail page, click **Export** > **Export JSON** to download the full JSON data for a single resource.

---

## Administration

Admin-only features are accessible from the **Admin** dropdown in the navbar.

### User Management

**Admin** > **Users** displays all registered accounts with:
- Username and email
- Role (Admin or Viewer)
- Authentication method (Local or LDAP)
- Account status (Active / Inactive)
- Last login timestamp

**Actions:**
- **Edit** -- Change a user's role (Admin/Viewer) or active status.
- **Deactivate** -- Disable an account without deleting it. Deactivated users cannot log in.

### System Settings

**Admin** > **Settings** provides:

**General:**
- **Allow self-registration** -- Toggle whether new users can register on their own. When disabled, only admins can create accounts.

**LDAP / Active Directory:**
- **Enable LDAP authentication** -- When enabled, users can log in with their AD/LDAP credentials.
- **LDAP Host** -- The LDAP server hostname (e.g. `ldap.example.com`).
- **Port** -- Default is 389 (or 636 for LDAPS).
- **Use SSL** -- Enable for LDAPS connections.
- **Base DN** -- The root of the LDAP directory (e.g. `dc=example,dc=com`).
- **User DN** -- The organizational unit containing users (e.g. `ou=Users`).
- **Login Attribute** -- The LDAP attribute to match for login (default: `sAMAccountName` for Active Directory).
- **Bind User DN** -- A service account DN for searching the directory.
- **Bind Password** -- The service account password (stored encrypted).

When LDAP is enabled, users who authenticate successfully via LDAP are automatically created in the local database on first login with the Viewer role. An admin can then promote them if needed.

### Server-Wide Default Credentials

**Admin** > **Default AWS** / **Default Azure**

These pages let you set up server-wide cloud credentials that all users inherit when they don't have their own personal connection for that provider. This is useful for shared environments where everyone queries the same cloud accounts.

The forms are identical to the personal connection forms. Only one default per provider can exist at a time; saving a new one replaces the previous default.

### Audit Log

**Admin** > **Audit Log** shows a chronological record of all security-relevant actions:

| Column | Description |
|--------|-------------|
| Timestamp | When the action occurred |
| User | Who performed it (or "System") |
| Action | The action type (login, register, create_connection, discover_resources, export_csv, etc.) |
| Target | The type of object affected (user, cloud_connection, etc.) |
| Details | Additional context in JSON format |
| IP Address | The client's IP address |

The log is paginated (50 entries per page) and ordered newest-first. Audit entries are append-only and cannot be modified or deleted through the application.

---

## Security & Architecture

### Credential Security

- Cloud credentials are **encrypted at rest** using Fernet symmetric encryption before being stored in the database.
- The encryption key (`FERNET_KEY`) is loaded from an environment variable and never stored in the database or source code.
- Credentials are **decrypted only in-memory** when needed for CLI execution, then immediately discarded.
- Credentials are passed to CLI commands via **environment variables**, never as command-line arguments (which would be visible in process listings).

### Authentication & Sessions

- Local passwords are hashed using **scrypt** (via Werkzeug).
- Sessions use **secure, HttpOnly, SameSite=Lax cookies** with an 8-hour lifetime.
- All forms are protected against **CSRF** attacks via Flask-WTF.
- AJAX requests include the CSRF token automatically via the `X-CSRFToken` header.

### CLI Execution Safety

- All cloud CLI commands are executed using Python's `subprocess.run()` with **argument lists** (never `shell=True`).
- A clean environment is constructed for each CLI call, containing only the necessary credential variables.
- Each command has a configurable **timeout** (default: 120 seconds) to prevent hanging.

### Change Password

Click your **username** in the top-right corner and select **Change Password**. You'll need to enter your current password and the new password. LDAP users cannot change their password through Native-Form (password changes are managed by the LDAP administrator).
