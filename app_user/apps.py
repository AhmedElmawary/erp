from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class AppUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_user'
    verbose_name = _('Users')

    def ready(self):
        import  app_user.signals