#!/usr/bin/env bash
set -euo pipefail

# Usage: sudo bash install-on-ec2.sh GIT_REPO_URL YOUR_DOMAIN [WWW=true]
# Example: sudo bash install-on-ec2.sh https://github.com/org/campushub-backend-2.git campushub360.xyz

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "Please run as root (use sudo)" >&2
  exit 1
fi

REPO_URL=${1:-}
DOMAIN=${2:-}
WWW=${3:-true}

if [[ -z "$REPO_URL" || -z "$DOMAIN" ]]; then
  echo "Usage: $0 REPO_URL DOMAIN [WWW=true]" >&2
  exit 1
fi

apt update && apt upgrade -y
apt install -y nginx python3-venv python3-pip git

id -u campushub &>/dev/null || adduser --system --group --home /srv/campushub campushub
mkdir -p /srv/campushub
chown campushub:campushub /srv/campushub

sudo -iu campushub bash -lc "
set -e
cd /srv/campushub
if [[ ! -d app/.git ]]; then
  git clone $REPO_URL app
fi
cd app
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
"

if [[ ! -f /etc/campushub.env ]]; then
  cp /srv/campushub/app/deploy/campushub.env.example /etc/campushub.env
  chmod 600 /etc/campushub.env
  echo "Edit /etc/campushub.env with your secrets before starting service." >&2
fi

cp /srv/campushub/app/deploy/campushub.service /etc/systemd/system/campushub.service
systemctl daemon-reload

# Install Nginx site
cp /srv/campushub/app/deploy/nginx/campushub.conf /etc/nginx/sites-available/campushub.conf
ln -sf /etc/nginx/sites-available/campushub.conf /etc/nginx/sites-enabled/campushub.conf
sed -i "s/campushub360.xyz/$DOMAIN/g" /etc/nginx/sites-available/campushub.conf
nginx -t
systemctl restart nginx

echo "Setup complete. Next steps:\n1) Edit /etc/campushub.env\n2) systemctl enable --now campushub\n3) (Optional) Install certbot and get TLS certs"


