from django.apps import AppConfig

class WardDataAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ward_data_app'
    # Updated verbose name for the admin panel
    verbose_name = 'Ward Data App'