# Architect Plus Deployment Package

This package contains all files needed to deploy Architect Plus in production.

## Quick Start

1. Copy all files to your server
2. Copy .env.template to .env and configure your API keys
3. Run: `python deploy.py`

## Docker Deployment

1. Configure .env file
2. Run: `docker-compose up -d`

## Manual Deployment

1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Configure .env file
5. Run: `gunicorn -c gunicorn.conf.py app:app`

## Systemd Service (Linux)

1. Copy architect-plus.service to /etc/systemd/system/
2. Update paths in service file
3. Run: `sudo systemctl enable architect-plus`
4. Run: `sudo systemctl start architect-plus`

## Health Check

Visit: http://your-server:5000/health
