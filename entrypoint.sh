#!/bin/bash
# entrypoint.sh

set -e

# Ensure correct permissions on volumes
# || true prevents script failure if directories don't exist yet
chown -R app:app /app/logs /app/pdfs /app/data /app/staticfiles || true

echo "Entrypoint started. Checking command: $1"

# If the command is 'celery', wait for RabbitMQ to be ready
if [ "$1" = 'celery' ]; then
    echo "Celery command detected. Waiting for RabbitMQ..."
    # Loop until a TCP connection to rabbitmq:5672 is successful
    while ! nc -z rabbitmq 5672; do
        echo "Waiting for RabbitMQ..."
        sleep 1
    done
    echo "RabbitMQ is ready!"
fi

# If the command is 'gunicorn' (web server), run database migrations
if [ "$1" = 'gunicorn' ]; then
    echo "Gunicorn command detected. Configuring Django application..."
    
    # Apply database migrations
    echo "Running 'manage.py migrate'..."
    python manage.py migrate --noinput
    
    # Collect all static files for Nginx to serve
    echo "Running 'manage.py collectstatic'..."
    python manage.py collectstatic --noinput --clear
fi

echo "Setup complete. Starting main process: $@"
exec "$@"