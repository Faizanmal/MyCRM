# Auto-register all models
from django.apps import apps
from django.contrib import admin

# Auto-register models via app.get_models()

app = apps.get_app_config('biofeedback_personalization')
for model in app.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
