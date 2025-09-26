import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("project.settings", namespace="CELERYD")

app.autodiscover_tasks()
