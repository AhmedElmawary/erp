from datetime import time, timedelta
from re import A, sub

from django.urls.base import reverse
from _helpers.admin import Amount
from django.db import models
from django.utils.translation import ugettext_lazy as _
from _helpers.models import COUNTRIES, client_img_upload_path, modified_num2words
from payment.models import ClientPaymentTransaction, Payment, PaymentTransactionType
from django.utils.html import format_html, format_html_join
from _helpers.models import PAYMENTTHODS
from django.utils import timezone


class Client(models.Model):
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _("Clients")

    name = models.CharField(_("name"), max_length=150)
    img = models.ImageField(_('User Image'), null=True,
                            blank=True, upload_to=client_img_upload_path)
    email = models.EmailField(
        _('User Email'), max_length=250, null=True, blank=True)
    phone = models.CharField(_('User Phone Number'),
                             max_length=20, unique=True)
    gender = models.IntegerField(verbose_name=_('Gender'), default=1, choices=[
                                 (1, _('male')), (2, _('female'))])
    address = models.CharField(_('User Address'), max_length=250)
    city = models.CharField(_('City name'), max_length=250, blank=True, default='Cairo')
    paying_method = models.IntegerField(
        _("Payment Method"), choices=PAYMENTTHODS, default=1)
    created_at = models.DateTimeField(
        _("Register at"), default=timezone.now, editable=False)
    country = models.CharField(
        _('country name'), null=True, choices=COUNTRIES, max_length=250 , default="EG")
    active_til = models.DateTimeField(
        _("Date of deactive the client"), default=None, null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    taxes = models.BooleanField(_("Taxes"), default=False)
    taxes_rate = models.PositiveBigIntegerField(_("Taxes Rate"), default=0.0,blank=True, null=True)
    cash = models.IntegerField(
        _("inital cash of account"),
        null=True, 
        blank=True, 
        default=0.0
    )   
    area = models.ForeignKey("area.Area", verbose_name=_("Area"), on_delete=models.DO_NOTHING)
    
    
    def num2ords_cash(self):
        return  modified_num2words(self.cash)
    
    def parsed_cash(self):
        return Amount.parse(self.cash)
    
    
    def clean_phone(self, *args, **kwargs) -> None:
        if not self.phone.isdigit():
            self.phone = f'0000000000{self.id}'

    def clean_name(self, *args, **kwargs):
        self.name = self.name.replace('/', '-')
        self.name = self.name.replace('\\', '-')

    def clean(self) -> None:
        self.clean_name()
        self.clean_phone()
        return super().clean()
    
    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return str(self.name)

    def period_close(self):
        return format_html('<button id=period_close  class=btn-primay>'+ _('period close') +'</button>', self.id)
    period_close.short_description = _('period close')

    def get_debit(self):
        payments =  self.transactions.filter(payment_type=1)
        return sum([payment.amount for payment in  payments])
    get_debit.short_description = _('Debit')

    def parsed_get_credit(self):
        return Amount.parse(self.get_credit())
    parsed_get_credit.short_description = _("Credit")
    
    def parsed_get_debit(self):
        return Amount.parse(self.get_debit())
    parsed_get_debit.short_description = _("Debit")
    
    def get_credit(self):
        payments =  self.transactions.filter(payment_type=2)
        return sum([payment.amount for payment in  payments])
    get_credit.short_description = _('Credit')

    def debit(self): 
       return  f'   ({Amount.parse(self.get_debit()) })  ' + modified_num2words(self.get_debit()) 
    debit.short_description = _('Debit')

    def credit(self):
       return  f' ({ Amount.parse(self.get_credit())})  ' + modified_num2words(self.get_credit())
    credit.short_description = _('Credit')

    def get_cash(self):
        net = self.prepare_net()
        if net < 0:
            return   _('credit')  +' '+_('with') +' '+  f'({ Amount.parse(abs(net)) }) '+ modified_num2words(abs(net))  
        return   _('debit')  +' '+_('with') +' '+  f'({ Amount.parse(abs(net))  }) ' + modified_num2words(abs(net)) 
    get_cash.short_description =_('Client balance')


    def prepare_net(self):
        return  self.get_debit() - self.get_credit() 

    def num2wods_prepare_net(self):     
        cash =  self.prepare_net()
        if  cash < 0:
            cash = abs(cash)
            return '-'+ modified_num2words(cash)
        return modified_num2words(cash)
    
    def parsed_prepare_net(self):
        cash = self.prepare_net() 
        return Amount.parse(cash) 
    
    def parsed_get_net(self):
        net = self.prepare_net() 
        net_str = Amount.parse(net) 
        if net > 0:
            net_str = Amount.parse(net) 
        return net_str
    parsed_get_net.short_description = _('Net')

    def parsed_get_net_label(self):
        net = self.prepare_net() 
        net_str = Amount.parse_with_label(net)
        if net > 0:
            net_str = Amount.parse_with_label(net) 
        return net_str
    parsed_get_net_label.short_description = _('Net')
    
    def account_statment_from(self):
        date_from = timezone.now().date()
        return format_html(f'<input type="date" class=account_statment_from name=date_from id="{self.id}:account_date_from" value="{date_from}" />')
    account_statment_from.short_description = _('account statment from')
        
    def account_statment_to(self):
        date_to = timezone.now().date() + timedelta(weeks=1)
        return format_html(f'<input type="date" class=account_statment_to name=date_to id="{self.id}:account_date_to" value="{date_to}" />')
    account_statment_to.short_description = _('account statment to')
    
    def account_statment_btn(self):
        date_from = timezone.now().date()
        date_to = timezone.now().date() + timedelta(weeks=1)
        url = reverse('admin:client_account_statment',
                      kwargs={
                            'date_from':date_from,
                            'date_to':date_to,
                            'client_id':self.id
                              })
        
        submit_btn = f'<a style="display:block; text-align: center" class="account_statment_btn button" id="{self.id}:account_statment_btn" class=btn href={url}> {_("print")} </a>'
        return format_html(submit_btn)
    account_statment_btn.short_description = _('account statment export')
    
    
    def get_net(self):
        net = self.prepare_net()
        net_str = f'{net} {_("credit")}'
        if net > 0:
            net_str = f'{net} {_("debit")}' 
        return net_str
    get_net.short_description = _('Net')

    def img_html(self):
        return format_html(
            f'<img src="/media/{self.img}" alt="supplier image" width=200px height=200px/>'
        )
    img_html.short_description = _("Image preview")

    def make_transaction(self):
        return format_html('<a class="button" href="{}">' + _("Make a transaction")+'</a>', f'{self.id}/make_a_transaction')
    make_transaction.short_description = _('make a transaction')
