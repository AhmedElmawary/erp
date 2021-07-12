from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class InvoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoice'
    verbose_name = _("Invoice")    
    def ready(self):
        import  invoice.signals
