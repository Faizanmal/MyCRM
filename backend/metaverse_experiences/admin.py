from django.contrib import admin
from .models import *

# Auto-register all models
from django.apps import apps

app = apps.get_app_config('metaverse_experiences')
for model in app.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
