#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Native-Form: Fedora 40 / RHEL 9 Server Setup Script
# =============================================================================

APP_USER="native-form"
APP_DIR="/opt/native-form"
LOG_DIR="/var/log/native-form"

echo "=== [1/8] System Update ==="
sudo dnf update -y

echo "=== [2/8] Install System Dependencies ==="
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    postgresql-server \
    postgresql-contrib \
    postgresql-devel \
    nginx \
    gcc \
    openldap-devel \
    openssl-devel \
    libffi-devel \
    redhat-rpm-config \
    unzip

echo "=== [3/8] Install AWS CLI v2 ==="
if ! command -v aws &>/dev/null; then
    cd /tmp
    curl -sL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi
echo "AWS CLI: $(aws --version)"

echo "=== [4/8] Install Azure CLI ==="
if ! command -v az &>/dev/null; then
    sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
    sudo dnf install -y https://packages.microsoft.com/config/rhel/9.0/packages-microsoft-prod.rpm || true
    sudo dnf install -y azure-cli
fi
echo "Azure CLI: $(az --version | head -1)"

echo "=== [5/8] Initialize and Configure PostgreSQL ==="
sudo postgresql-setup --initdb || true
sudo systemctl enable --now postgresql

PG_HBA="/var/lib/pgsql/data/pg_hba.conf"
if ! sudo grep -q "native_form" "$PG_HBA" 2>/dev/null; then
    echo '# Native-Form application database' | sudo tee -a "$PG_HBA"
    echo 'host native_form native_form_user 127.0.0.1/32 scram-sha-256' | sudo tee -a "$PG_HBA"
    sudo systemctl reload postgresql
fi

# Create database user and database
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='native_form_user'" \
    | grep -q 1 || sudo -u postgres psql -c "CREATE USER native_form_user WITH PASSWORD 'CHANGE_ME_IN_PRODUCTION';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='native_form'" \
    | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE native_form OWNER native_form_user;"

echo "=== [6/8] Create Application User and Directory ==="
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd --system --shell /sbin/nologin --home-dir "$APP_DIR" "$APP_USER"
fi
sudo mkdir -p "$APP_DIR" "$LOG_DIR"
sudo chown "$APP_USER":"$APP_USER" "$APP_DIR" "$LOG_DIR"

echo "=== [7/8] Set Up Python Virtual Environment ==="
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip

if [ -f "$APP_DIR/requirements.txt" ]; then
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

echo "=== [8/8] Configure Nginx and Systemd ==="
if [ -f "$APP_DIR/deploy/nginx.conf" ]; then
    sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/conf.d/native-form.conf
    sudo nginx -t
    sudo systemctl enable --now nginx
fi

if [ -f "$APP_DIR/deploy/native-form.service" ]; then
    sudo cp "$APP_DIR/deploy/native-form.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable native-form
fi

# Firewall
sudo firewall-cmd --permanent --add-service=http 2>/dev/null || true
sudo firewall-cmd --permanent --add-service=https 2>/dev/null || true
sudo firewall-cmd --reload 2>/dev/null || true

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Copy application code to $APP_DIR"
echo "  2. Create $APP_DIR/.env from .env.example"
echo "  3. Generate keys:"
echo "     python3 -c \"import secrets; print(secrets.token_hex(32))\""
echo "     python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
echo "  4. Add SECRET_KEY and FERNET_KEY to $APP_DIR/.env"
echo "  5. Change the PostgreSQL password in .env"
echo "  6. Initialize the database:"
echo "     cd $APP_DIR && sudo -u $APP_USER venv/bin/flask db upgrade"
echo "  7. Start the service:"
echo "     sudo systemctl start native-form"
echo "  8. Set up TLS certificates for Nginx"
