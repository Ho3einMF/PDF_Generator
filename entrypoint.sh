#!/bin/bash

# Start celery workers
make celery_worker &

# Start gunicorn
exec gunicorn
