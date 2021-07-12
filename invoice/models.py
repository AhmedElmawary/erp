from django.db import models
from django.db.models import fields
from django.db.models.deletion import DO_NOTHING
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from payment.models import Payment


# class Order(models.Model):
#     class Meta:
#         verbose_name = _('Order')
#         verbose_name_plural = _("Orders")

#     def cost(slef):
#         pass

#     def cost_after_discount(self):
#         pass

#     discount = models.ForeignKey("item.Discount", null=True, blank=True, verbose_name=_(
#         "Discount"), on_delete=models.DO_NOTHING)
#     is_order = models.BooleanField(_("Is order"), default=True)
#     status = models.ForeignKey("item.Status", verbose_name=_(
#         "Status"), on_delete=models.DO_NOTHING)
#     payment = models.ForeignKey("payment.Payment", verbose_name=_(
#         "payment"), on_delete=models.DO_NOTHING, )
#     issued_at = models.DateTimeField(_("Issued at"), default=timezone.now)
#     note = models.TextField(_("Note"), blank=True, null=True)
#     reference = models.CharField(
#         _("reference"), max_length=250, default='', null=True, blank=True)
#     items = models.ManyToManyField(
#         "item.Item", verbose_name=_("Items"), through='OrderItem')

#     def get_items(self):
#         return [item for item in self.items.through.objects.all()]

#     def items_cost(self):
#         return sum([item.price * item.quantity for item in self.get_items()])

#     def items_names(self):
#         return [row.item.name for row in self.get_items()]

#     def items_names_html(self):
#         html = format_html('<table><thead>', '')
#         html+= format_html_join('\n', "<tr><th>{}</th></tr>", 
#         ((name, )for name in self.items_names())
#         )
#         html+= format_html('</thead></table>')
      
#         return html
#     items_names_html.short_description = 'Items of the order'


#     def payment_method(self):
#         return str(self.payment)

#     def __str__(self):
#         return str(self.id)



# class OrderItem(models.Model):  
#     item = models.ForeignKey("item.Item", verbose_name=_(
#         "Item"), on_delete=models.DO_NOTHING)
#     order = models.ForeignKey("invoice.Order", verbose_name=_(
#         "Order"), on_delete=models.DO_NOTHING)
#     quantity = models.IntegerField(_("Quantity"), default=0)
#     price = models.FloatField(_("Price"), max_length=150, default=0.0)
#     supplier_price = models.FloatField(_("Supplier Price"), default=0.0)
#     discount = models.ForeignKey("item.Discount", verbose_name=_(
#         "Discount"), on_delete=models.DO_NOTHING, null=True, blank=True)

#     def __str__(self):
#         return str(self.item) + ' for order ' + str(self.order)

#     def cost_per_item(self):
#         return self.price * self.quantity if self.price else 0

#     def cost_per_item_supplier(self):
#         return self.supplier_price * self.quantity if self.supplier_price else 0


# class SupplierOrder(Order):
#     class Meta:
#         verbose_name = _('Supplier order')
#         verbose_name_plural = _('Supplier orders')

#     supplier = models.ForeignKey("supplier.Supplier", verbose_name=_(
#         "Supplier"), null=True, blank=True, on_delete=models.DO_NOTHING)
#     invoice = models.ForeignKey("invoice.SupplierInvoice", verbose_name=_(
#         "Invoice"), on_delete=models.DO_NOTHING)

#     def cost(self):
#         return sum(self.items.price * self.items.quantity) if self.items.price else 0


# class ClientOrder(Order):
#     class Meta:
#         verbose_name = _('Client order')
#         verbose_name_plural = _('Client orders')

#     client = models.ForeignKey("client.Client", verbose_name=_(
#         "Client"), null=True, blank=True, on_delete=models.DO_NOTHING)
#     invoice = models.ForeignKey("invoice.ClientInvoice", verbose_name=_(
#         "Invoice"), on_delete=models.DO_NOTHING)

#     def cost(self):
#         return sum(self.items.price * self.items.quantity) if self.items.price else 0


# class Invoice(models.Model):
#     def ends_at_after_week():
#         return timezone.now() + timedelta(days=7)

#     status = models.ForeignKey("item.Status", verbose_name=_(
#         "Invoice Status"), on_delete=DO_NOTHING)
#     ends_at = models.DateTimeField(_("Ends At"), default=ends_at_after_week)
#     issued_at = models.DateTimeField(_('Issued_at'), default=datetime.now)
#     fully_paid = models.BooleanField(_("Is Paid"), default=False)

#     def __str__(self):
#         return str(self.id)


# class SupplierInvoice(Invoice):
#     class Meta:
#         verbose_name = _('Supplier Invoice')
#         verbose_name_plural = _("Supplier Invoices")

#     supplier = models.ForeignKey("supplier.Supplier", verbose_name=_(
#         "Supplier"), on_delete=models.DO_NOTHING)


# class ClientInvoice(Invoice):
#     class Meta:
#         verbose_name = _('Client Invoice')
#         verbose_name_plural = _("Client Invoices")

#     client = models.ForeignKey("client.Client", verbose_name=_(
#         "Client"), on_delete=models.DO_NOTHING)
#     required_money = models.ForeignKey("invoice.ToBePaidClientInvoice", verbose_name=_(
#         "Remaining Money"), on_delete=models.DO_NOTHING, null=True, blank=True)


# class ToBePaidClientInvoice(models.Model):
#     order = models.ForeignKey("invoice.ClientOrder", verbose_name=_(
#         "Order"), on_delete=models.DO_NOTHING)
#     amount = models.FloatField(_("Required Amount"), default=0.0)

#     def __str__(self):
#         return self.amount
