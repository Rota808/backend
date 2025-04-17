#!/bin/bash
export PYTHONPATH="/home/site/wwwroot/backend/back:$PYTHONPATH"
cd /home/site/wwwroot/backend/back
gunicorn --bind 0.0.0.0:8000 back.back.wsgi