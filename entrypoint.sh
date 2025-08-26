#!/bin/bash
set -e

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run Django database migrations
# echo "Running database migrations..."
# python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Function to run Django background tasks
# run_process_tasks() {
#     echo "Starting Django background task process..."
#     python manage.py process_tasks &
# }

# # Start the Django background tasks in a separate thread
# run_process_tasks

# Start uvicorn as the main process
echo "Starting uvicorn server..."
python manage.py process_tasks &
exec uvicorn manipalapp.wsgi:application --host 0.0.0.0 --port 8000 --workers 2 
# --worker-class uvicorn.workers.UvicornWorker
exec "$@"