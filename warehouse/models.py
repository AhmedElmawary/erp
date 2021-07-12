from os import name
from django.db import models
from django.utils.translation import gettext_lazy as _

class Manager(models.Model):

    name = models.CharField(_("Name"), max_length=250)
    phone = models.CharField(_("Phone number"),max_length=250, null=True, blank=True)
    additional_phone =  models.CharField(_("Additinol phone number"),max_length=250, null=True, blank=True)
    email = models.EmailField(_("Email"), max_length=254, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = _('Manager')
        verbose_name_plural = _('Managers')


class Warehouse(models.Model):
  
    name = models.CharField(_("Name"), max_length=250)
    address = models.TextField(_("Address"))
    area = models.ForeignKey("area.Area", verbose_name=_("Area"), on_delete=models.DO_NOTHING)
    openinig = models.TimeField(_("Opening time"), null=True, blank=True)
    closing = models.TimeField(_("Closing time"), null=True, blank=True)
    executive = models.ForeignKey("Manager", verbose_name=_("Warehouse manager"), on_delete=models.DO_NOTHING) 

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')
