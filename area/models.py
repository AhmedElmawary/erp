from django.db import models
from django.utils.translation import gettext_lazy as _

class Area(models.Model):
    name = models.CharField(_("name"), unique=True,max_length=250)

    def __str__(self) -> str:
        return str(_(self.name))

    class Meta:
        verbose_name = _('Area')
        