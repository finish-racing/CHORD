# CHORD Installer System v1

This package continues from Wave D2 and adds the Ubuntu installer / upgrade / rollback / reset layer for CHORD.

## Included
- install bootstrap script
- release deployment script
- rollback script
- soft reset and hard reset helpers
- systemd service file
- environment template
- Nginx site template
- PostgreSQL bootstrap SQL
- operator install/upgrade/rollback documentation

## Target layout
- `/opt/chord/releases/<version>/`
- `/opt/chord/current`
- `/etc/chord/config.toml`
- `/etc/chord/chord.env`
- `/var/lib/chord/...`
- `/var/log/chord/...`
