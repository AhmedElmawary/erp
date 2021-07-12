from datetime import datetime
from _helpers.admin import Amount
from django.db import models
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.translation import gettext, ugettext_lazy as _
from django.utils import timezone
from _helpers.models import (
    CURRENCIES, PAYMENTTHODS, PAYMENTTYPES, TRANSACTION_TYPES, modified_num2words)

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime


class Payment(models.Model):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _("Paymentes")

    issued_at = models.DateTimeField(_("Issued at"), default=datetime.today)
    status = models.ForeignKey("item.Status", verbose_name=_(
        "Status"), on_delete=models.DO_NOTHING)
    # method  =   models.ForeignKey("payment.Method", verbose_name=_("Method"), on_delete=models.DO_NOTHING)
    method = models.IntegerField(
        _("Payment method"), default=1, choices=PAYMENTTHODS, max_length=2)

    amount = models.CharField(_("Amount Paid"), validators=[
                              MinValueValidator(0.0)], max_length=50)
    currency = models.IntegerField(
        verbose_name=_('Currency'), choices=CURRENCIES, default=1)

    def __str__(self):
        return str(PAYMENTTHODS[self.method - 1][-1])


class PaymentTransactionType(models.Model):
    name = models.CharField(_("Payment Type"), max_length=50, unique=True)
    transaction_for = models.IntegerField(
        _("which type is related"), 
        choices=PAYMENTTYPES)
    for_supplier= models.BooleanField(_("For supplier"), default=False)
    for_client  = models.BooleanField(_("For client"), default=False)
    
    def __str__(self) -> str:
        return gettext(str(self.name))

    def clean(self) -> None:
        self.name = self.name.strip()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)


class PaymentTransaction(models.Model):
    file_transaction = models.FileField(
        _("File"), upload_to=None, max_length=100, null=True, blank=True)

    payment_type = models.IntegerField(
        _("Payment transaction Type"), choices=PAYMENTTYPES, default=1)

    description = models.TextField(_("Description"),  null=True, blank=True)
    amount = models.PositiveBigIntegerField(_("amount"), validators=[
                                            MinValueValidator(0.0), MaxValueValidator(9999999.0)], )
    currency = models.IntegerField(verbose_name=_('Currency'), choices=CURRENCIES, default=1)
    issued_at = models.DateTimeField(
        _("Issued at"), 
        default=timezone.now, 
        editable=False
        )

    type_tranasction = models.ForeignKey("PaymentTransactionType", verbose_name=_("Transaction type"), on_delete=models.DO_NOTHING)

    issued_by =  models.ForeignKey("app_user.User", verbose_name=_("Issuer"), on_delete=models.DO_NOTHING)
    
    def parsed_amount(self):
        return " {:,.2f}  ".format(self.amount) 
    parsed_amount.short_description = _('amount')
    
    def amount_currency(self):
        return self.parsed_amount() + _("egp") 
    amount_currency.short_description = _('amount')
    
    def amount_to_float(self):
        return self.amount / 100

    def __str__(self) -> str:
        return str(PAYMENTTYPES[self.payment_type - 1][-1])

    def str_amount(self):
        amount = modified_num2words(self.amount)
        return format_html(f'<span  id="str_amount"> {amount} </span>')
    str_amount.short_description = _('transaction amount')

    def issued_at_int(self):
        return  self.issued_at.strftime('%H:%I:%S -- %d-%m-%Y')
    issued_at_int.short_description = _('issued at')
    
    def issued_at_day(self):
        return _(self.issued_at.strftime('%A'))

    def issued_at_day_date(self):
        return f'{naturalday(self.issued_at_day())} {self.issued_at_int()}'

class ClientPaymentTransaction(PaymentTransaction):
    class Meta:
        verbose_name = _("Client payment transaction")
        verbose_name_plural = _("Client payment transactions")

    client = models.ForeignKey("client.Client", verbose_name=_(
        "Client"), on_delete=models.DO_NOTHING, related_name='transactions')

    def make_cash_after_str(self):
        return format_html('<div id=cash_after_str>{}</div>', 0)
    make_cash_after_str.short_description = _(
        "client balance after transaction")

    def client_cash_after_transaction(self):
        if self.payment_type == 1:
            cash = self.supplier.prepare_net()
        else:
            cash = self.supplier.prepare_net() - self.amount
            if cash < 0:
                cash = abs(cash)
                return '- '+Amount.parse(cash)
        return cash    
    client_cash_after_transaction.short_description = _('client Cash after transaction')


    def client_cash(self):
        return self.client.prepare_net() if self.client.prepare_net() else 0
        
    def abs_client_cash(self):
        return abs(self.client_cash()) 

    def parsed_client_cash(self):
        return Amount.parse(self.abs_client_cash())
    
    def n2umwords_client_cahs(self):
        return modified_num2words(self.abs_client_cash())
    
    def client_cash_html(self):
        return  '( '+self.parsed_client_cash() + ') ' +  self.n2umwords_client_cahs()
    client_cash_html.short_description = _('client cash')

    def __str__(self) -> str:
        return _('transaction for ')  +'  '+ str(self.client) +'  '+str(self.issued_at.strftime('%H:%I:%S -- %Y-%m-%d'))

    def print_transaction(self):
        url = reverse('admin:client_print_transaction', args=[self.id])
        return format_html("<a class='button' data-href='{}' id=print_transaction > {} </a>", url, _("print transaction"))
    print_transaction.short_description = _("print_transaction")
    
    def issued_at_day_date(self):
        return f'{naturalday(self.issued_at_day())} {self.issued_at_int()}'

    def issued_at_day(self):
        return _(self.issued_at.strftime('%A'))
    
    def send_to_printer(self):
        url = reverse('admin:send_to_print_transaction', args=[self.id])
        return format_html("<button class='button' href='{}'> {} </button>", url, _("print transaction"))


class SupplierPaymentTransaction(PaymentTransaction):
    class Meta:
        verbose_name = _("Supplier payment transaction")
        verbose_name_plural = _("Supplier payment transactions")

    items = models.ManyToManyField("item.Item", verbose_name=_(
        "Item of the transactions if there are any"), through='OrderItem')
    supplier = models.ForeignKey("supplier.Supplier", verbose_name=_(
        "Supplier"), on_delete=models.DO_NOTHING, related_name='transactions')

    def get_items(self):
        return [item for item in self.items.through.objects.all()]

    def items_cost(self):
        total_cost = sum(
            [item.supplier_price * item.quantity for item in self.get_items()])
        return modified_num2words(Amount.parse(total_cost))

    items_cost.short_description = _("total cost for the items")

    def supplier_cash_after_transaction(self):
        if self.payment_type == 1:
            cash = self.supplier.prepare_net()
        else:
            cash = self.supplier.prepare_net() - self.amount
            if cash < 0:
                cash = abs(cash)
                return '- '+cash
        return cash
    supplier_cash_after_transaction.short_description = _(
        'Supplier Cash after transaction')

    def supplier_cash(self):
        return self.supplier.prepare_net() if self.supplier.prepare_net() else 0
        
    def abs_supplier_cash(self):
        return abs(self.supplier_cash()) 

    def parsed_supplier_cash(self):
        return Amount.parse(self.abs_supplier_cash())
    
    def n2umwords_supplier_cahs(self):
        return modified_num2words(self.abs_supplier_cash())
    
    def supplier_cash_html(self):
        return  '( '+self.parsed_supplier_cash() + ') ' +  self.n2umwords_supplier_cahs()
    supplier_cash_html.short_description = _('supplier cash')
    
    
    def __str__(self) -> str:
        return _('transaction for ')  +' '+ str(self.supplier) +'  '+str(self.issued_at.strftime('%H:%I:%S -- %Y-%m-%d'))

    def print_transaction(self):
        url = reverse('admin:supplier_print_transaction', args=[self.id])
        return format_html("<a class='button' data-href='{}' id=print_transaction > {} </a>", url, _("print transaction"))
    print_transaction.short_description = _("print_transaction")


class OrderItem(models.Model):
    class Meta:
        verbose_name = _('Transaction Items')
        verbose_name_plural = _('Transaction Items')

    item = models.ForeignKey("item.Item", verbose_name=_(
        "Item"), on_delete=models.DO_NOTHING)
    transaction = models.ForeignKey("SupplierPaymentTransaction", verbose_name=_(
        "transaction"), on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(_("Quantity"), default=0)
    price = models.PositiveBigIntegerField(
        _("Price"), max_length=150, default=0.0)
    supplier_price = models.PositiveBigIntegerField(
        _("Supplier Price"), default=0.0)
    discount = models.ForeignKey("item.Discount", verbose_name=_(
        "Discount"), on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return str(self.item)

    def cost_per_item(self):
        cost = self.price * self.quantity if self.price else 0
        return modified_num2words(cost)

    def cost_per_item_supplier(self):
        return self.supplier_price * self.quantity if self.supplier_price else 0
    cost_per_item_supplier.short_description = _('cost per item')
