from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class SupplierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'supplier'
    verbose_name = _("Supplier")
    def ready(self):
        pass
        # import supplier.signals
