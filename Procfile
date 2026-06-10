web: uvicorn api.routes:app --host 0.0.0.0 --port $PORT
worker: celery -A app.app_data_sources.tasks worker --loglevel=INFO
