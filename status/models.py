from django.db import models
from django.utils.translation import ugettext_lazy as _

class Option(models.Model):
    class Meta:
        verbose_name = _('Option')
        verbose_name_plural = _("Options")
  
    name  = models.CharField(_("Status"), max_length=150, unique=True)

    def save(self, *args, **kwargs):
        self.name = str(self.name).lower()
        super(Option, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.name).capitalize()



class Status(models.Model):
    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _("Statuses")

    name  = models.CharField(_("Status"), max_length=150, unique=True)
    

    def save(self,*args, **kwargs):
        self.name = str(self.name).lower()
        super(Status, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name).capitalize()



class Type(models.Model):
    class Meta:
        verbose_name = _('Type')
        verbose_name_plural = _("Types")

    name  = models.CharField(_("Type"), max_length=150, unique=True)
   

    def save(self, *args, **kwargs):
        self.name = str(self.name).lower()
        super(Type, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name).capitalize()


class Variation(models.Model):
    class Meta:
        verbose_name = _('Variation')
        verbose_name_plural = _("Variations")

    types   =   models.ForeignKey("status.Type", verbose_name=_("Type"), on_delete=models.DO_NOTHING)
    option  =   models.ForeignKey("status.Option", verbose_name=_("Option"), on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{str(self.types)} {str(self.option)}'

