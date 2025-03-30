#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn processes
echo "Starting Gunicorn"
gunicorn baruchstreks.wsgi:application --bind=0.0.0.0:8000
