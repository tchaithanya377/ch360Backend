Deployment: EC2 + Nginx + Gunicorn

Overview
- Nginx serves /static/ and /media/ and proxies to Gunicorn on 127.0.0.1:8000
- Systemd manages the Django app via run-gunicorn.sh
- Certbot (optional) for HTTPS

Prerequisites
- Ubuntu 22.04 EC2 instance with ports 80/443 open in the security group
- PostgreSQL reachable (RDS or self-managed)
- A DNS domain pointed to the EC2 public IP

1) Install system packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx python3-venv python3-pip git
```

2) Create app user and directories
```bash
sudo adduser --system --group --home /srv/campushub campushub
sudo mkdir -p /srv/campushub
sudo chown campushub:campushub /srv/campushub
```

3) Clone and install Python deps
```bash
sudo -iu campushub bash -lc '
cd /srv/campushub
git clone YOUR_REPO_URL app
cd app
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
'
```

4) Configure environment
```bash
sudo cp /srv/campushub/app/deploy/campushub.env.example /etc/campushub.env
sudo nano /etc/campushub.env   # edit secrets and hosts
sudo chmod 600 /etc/campushub.env
```

5) Install systemd service
```bash
sudo cp /srv/campushub/app/deploy/campushub.service /etc/systemd/system/campushub.service
sudo systemctl daemon-reload
sudo systemctl enable --now campushub
sudo systemctl status campushub | cat
```

6) Configure Nginx
```bash
sudo cp /srv/campushub/app/deploy/nginx/campushub.conf /etc/nginx/sites-available/campushub.conf
sudo ln -sf /etc/nginx/sites-available/campushub.conf /etc/nginx/sites-enabled/campushub.conf
sudo nginx -t
sudo systemctl restart nginx
```

7) Optional: TLS with Certbot
```bash
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN --agree-tos -m YOUREMAIL --non-interactive
sudo certbot renew --dry-run
```

8) Deploy updates later
```bash
sudo -iu campushub bash -lc '
cd /srv/campushub/app
git pull
. .venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
'
sudo systemctl restart campushub
```

Paths
- App: /srv/campushub/app
- Static: /srv/campushub/app/static
- Media: /srv/campushub/app/media

Logs
- App: journalctl -u campushub -f
- Nginx: /var/log/nginx/error.log


