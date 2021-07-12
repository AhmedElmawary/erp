from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields.related import ForeignKey
import warehouse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from _helpers.models import (get_discount, product_img_upload_path, product_banner_upload_path)
from django.core.validators import MaxValueValidator, MinValueValidator
from _helpers.models import DISTCOUNT_TYPES, uuid4

class Item(models.Model):
    ITEM_UNITES = [
        (1, 'M'),
        (2, 'G'),
    ]

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
    
    label           =   models.CharField(_("Label"), max_length=250)
    name            =   models.CharField(_("name"), max_length=250)
    price           =   models.FloatField(_("Price of an item"),validators=[MinValueValidator(0)],default=0.0)
    details         =   models.TextField(_("Details"), null=True, blank=True)
    unit            =   models.IntegerField(_("Unit"), choices=ITEM_UNITES, default=1)
    variation       =   models.ManyToManyField("item.Variation", verbose_name=_("Variation"))
    image           =   models.ImageField(_("Image"), upload_to=product_img_upload_path, blank=True, null=True)
    banner          =   models.ImageField(_("Banner"), upload_to=product_banner_upload_path, blank=True, null=True)
    tax             =   models.FloatField(_("Tax"), default=0.0, blank=True, null=True)
    serial_no       =   models.IntegerField(_("Serial Number"), default=00000)
    supplier_price  =   models.FloatField(_("Supplier price"), default=0.0)
    note            =   models.TextField(_("Desctiption"), default='item ...')
    optional        =   models.BooleanField(_("Is optional"), default=False)
    data            =   models.JSONField(_("Item as Json"), blank=True, null=True)
    warehouse       =   models.ForeignKey('warehouse.Warehouse', on_delete=DO_NOTHING, verbose_name=_('Warehouse'))
    
    # vat             =   models.ForeignKey("item.Vat", verbose_name=_("Vat"), on_delete=models.DO_NOTHING)
    # ctx             =   models.ForeignKey("item.CTX", verbose_name=_("CTX"), on_delete=models.DO_NOTHING)
    # discount        =   models.ForeignKey("item.Discount", verbose_name=_("Discount"), on_delete=models.DO_NOTHING, null=True, blank=True)


    def cost_per_item(self):
        return self.price * self.quantity
    cost_per_item.short_description =  _('cost_per_item')

    def cost_per_item_supplier(self):
        return self.supplier_price * self.quantity
    cost_per_item.short_description =  _('cost_per_item')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        self.data = {
            '_id': uuid4(),
            'label': self.label,
            'name': self.name,
            'price': self.price,
            'details': self.details,
            'unit': self.unit,
            'variation': self.variation,
            'image': self.image,
            'banner': self.banner,
            'tax': self.tax,
            'serial_no': self.serial_no,
            'supplier_price': self.supplier_price,
            'note': self.note,
            'optional': self.optional,
        }
        return super().save(*args, **kwargs)    

class SupplierItem(models.Model):
    supplier = models.ForeignKey("supplier.Supplier", verbose_name=_("Supplier"), on_delete=models.DO_NOTHING)
    item     = models.ForeignKey("item.Item", verbose_name=_("Item"), on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(_("Quantity") ,default=0)
    note     = models.TextField(_("Desctiption"), default='...')

    def __str__(self):
        return str(self.item)


class ItemFile(models.Model):
    item = models.ForeignKey("item.Item", verbose_name=_("Item"), on_delete=models.DO_NOTHING)
    filename = models.CharField(_("Filename"), max_length=50)
    path = models.CharField(_("Path"), max_length=50)
     

class Category(models.Model):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    name = models.CharField(_("Name"), max_length=50)

    def __str__(self):
        return self.name
    
class Option(models.Model):
    class Meta:
            verbose_name = _("Option")
            verbose_name_plural = _("Options")

    title = models.CharField(_("Title"), max_length=50)

    def __str__(self):
        return str(self.title)
    

class Variation(models.Model):
    class Meta:
            verbose_name = _("Variation")
            verbose_name_plural = _("Variations")

    category = models.ForeignKey("item.Category", verbose_name=_("Category"), on_delete=models.DO_NOTHING)
    option = models.ForeignKey("item.Option", verbose_name=_("Option"), on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.category} - {self.option}'
    
    
class Discount(models.Model):
    class Meta:
            verbose_name = _("Discount")
            verbose_name_plural = _("Discounts")

    title   = models.IntegerField(_('Type'), choices=DISTCOUNT_TYPES, default=1)
    amount  = models.IntegerField(_("Rate"))

    def __str__(self):
        return f'{self.amount} {get_discount(self.title)}'  
    
class Vat(models.Model):
    number = models.IntegerField(_("Number"), default=1)
    name   = models.CharField(_("Name"), max_length=250)
    label  = models.CharField(_("Display Name"), max_length=250, )

    def __str__(self):
        return str(self.label)
    

class Status(models.Model):
    number = models.IntegerField(_("Number"), )
    name = models.CharField(_("Name"), max_length=250)
    label = models.CharField(_("Display Name"), max_length=250, )

    def __str__(self):
        return str(self.label)


# class CTX(models.Model):
#     class Meta:
#         verbose_name = _("CTX")
#         verbose_name_plural = _("CTX")
#     name = models.CharField(_("Name"), max_length=250)

#     def __str__(self):
#         return self.name
    