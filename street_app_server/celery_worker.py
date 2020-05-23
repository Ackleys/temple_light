import os

from app import create_app, celery

print("celery_worker.py")

# gevent.monkey.patch_all()

cfg = os.getenv('FLASK_CONFIG') or 'default'
print(cfg)

app = create_app(cfg)
app.app_context().push()