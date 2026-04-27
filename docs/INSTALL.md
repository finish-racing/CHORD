# CHORD Install Guide

## Fresh install
1. Copy the release package to the Ubuntu laptop.
2. Extract it.
3. From the extracted directory, run:
   `RELEASE_VERSION=0.1.0 bash installer/install_chord.sh`
4. Edit:
   - `/etc/chord/chord.env`
   - `/etc/chord/config.toml`
5. Bootstrap PostgreSQL:
   `sudo -u postgres psql -f /opt/chord/current/installer/postgresql_bootstrap.sql`
6. Initialize schema:
   `sudo -u chord /opt/chord/current/.venv/bin/chord initdb --config /etc/chord/config.toml`
7. Install Nginx site if desired:
   - copy `installer/nginx_chord.conf` to `/etc/nginx/sites-available/chord`
   - enable it and reload nginx
8. Start CHORD:
   `sudo systemctl enable --now chord-web`

## Verification
- Web: `http://<ubuntu-host>:8000/`
- Health: `http://<ubuntu-host>:8000/health`
