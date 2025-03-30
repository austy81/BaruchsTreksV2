#!/bin/bash

# Start Gunicorn processes
echo "Starting Gunicorn"
gunicorn baruchstreks.wsgi:application --bind=0.0.0.0:8000
