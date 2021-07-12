from datetime import time
from django import forms
from app_user.models import ClosingPeriod
from django.utils import timezone
import xlsxwriter
from xhtml2pdf import pisa
from payment.models import PaymentTransactionType, SupplierPaymentTransaction
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.urls.resolvers import URLPattern
from typing import Any, Dict, List, Optional, Tuple, Union
from django.http.request import HttpRequest
from django.contrib import admin
from django.http.response import HttpResponse,  HttpResponseRedirect
from django.urls.base import reverse
from django.urls.conf import path
from .models import Supplier
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.html import format_html
from _helpers.admin import Amount, CommonMethods, TempSupplier as SupplierHelper, ConsumerTransactionDownloder, admin_supplier_download_transaction_pdf, make_xls_data, make_xls_headers, str_to_date
from _helpers.models import areas_ar_en,  find_in, get_currency, get_payment_type, modified_num2words
from _helpers.admin import ConsumerTransaction
from django.template.loader import render_to_string
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from zipfile import ZipFile
import json, os

class SupplierChange(forms.ModelForm):
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
    class Meta :
        model=Supplier
        fields = ['date_from', 'date_to']

class SupplierAdmin(admin.ModelAdmin):
    form = SupplierChange
    class Media:
        js = (
            'account_statment.js',
            'supplier_transactions.js',
            )

    add_fieldsets = (
        (ugettext_lazy('Main info'), {
            'classes': ("wide",),
            "fields": (
            _('id'),
            _('name'),
            _('email'),
            _('phone'),
            _('gender'),
            _('img'),

            ),
        }),
        (ugettext_lazy("Location"), {
            'classes': ('collapse', 'wide'),
            'fields': (
            _('country'),
            _('area'),
            _('city'),
            _('address'),
            )
        })
        ,(ugettext_lazy('Cash'), {
            'classes': ('collapse', 'wide'),
            "fields" : (
                _('debit'),
                _('credit'),
                _('get_cash'),
                _('cash'),
                
            )
        }),(ugettext_lazy('Taxes'), {
            "classes": ('collapse', 'wide'),
            'fields' :
            (
                _('taxes'),
                _('taxes_rate'),
            )
            }),
        (ugettext_lazy('Status'), {'classes': ('collapse',),"fields": ('is_active',)})
    )

    fieldsets = (
        (ugettext_lazy('Main info'), {
            'classes': ("wide",),
            "fields": (
            _('id'),
            _('name'),
            _('email'),
            _('phone'),
            _('gender'),
            _('img'),

            ),
        }),
        (ugettext_lazy("Location"), {
            'classes': ('collapse', 'wide'),
            'fields': (
            _('country'),
            _('area'),
            _('city'),
            _('address'),
            )
        })
        ,(ugettext_lazy('Cash'), {
            'classes': ('collapse', 'wide'),
            "fields" : (
                _('debit'),
                _('credit'),
                _('get_cash'),
                _('period_close'),
                
            )
        }),(ugettext_lazy('Taxes'), {
            "classes": ('collapse', 'wide'),
            'fields' :
            (
                _('taxes'),
                _('taxes_rate'),
            )
            }),
        (ugettext_lazy('Status'), {'classes': ('collapse',),"fields": ('is_active',)})
    )
    'email',

    list_display = (
        'id',
        'name',
        'phone',
        'area',
        'parsed_get_debit',
        'parsed_get_credit',
        'parsed_get_net',
        'taxes',
        'is_active',
        # 'make_transaction',
    'account_statment_from',
    'account_statment_to',
    'account_statment_btn',
    )
    
    actions = [
        _('activate'),
        _('deactivate'),
        _('export_as_xls'),
        _('export_invoices_for'),
        ]
        
    list_filter = ('is_active', 'taxes', 'cash', 'transactions__issued_at')
    search_fields = ['name', 'email', 'phone','transactions__issued_at', 'area__name']
    list_display_links = ['name']

    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> Tuple[QuerySet, bool]:
        area = find_in(areas_ar_en(), search_term)
        if area:
            search_term = area[search_term]

        return super().get_search_results(request, queryset, search_term)

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any]=None) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any]=None) -> bool:
        return super().has_change_permission(request, obj=obj)


    change_form_template = 'admin/supplier/supplier/custom_change_form.html'
    change_list_template = 'admin/supplier/supplier/custom_change_list.html'

    def changelist_view(self, request: HttpRequest, extra_context: Optional[Dict[str, str]]=None) -> TemplateResponse:
        extra_context = {
            'to': _('to'),
            'from': _('from'),
            'export': _('export'),
            "account_stament_label": _('account statment')
        }

        response  = super().changelist_view(request, extra_context=extra_context)
        if request.COOKIES.get('supplier_id'):
            response.delete_cookie('supplier_id')

        return response

    def account_statment(self, request, date_from, date_to, suppliers):
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition']= 'attachment; filename=account_statments.zip'
        zipfile = ZipFile(response,'w')
        date_from = str_to_date(date_from)
        date_to = str_to_date(date_to)
        suppliers_ids = suppliers.split(":")
        suppliers = Supplier.objects.filter(id__in=suppliers_ids)
        for supplier in  suppliers.all():
            file_name = SupplierHelper.new_account_statment_pdf(supplier, date_from=date_from, date_to=date_to)
            if file_name:
                zipfile.write(file_name)
                os.remove(file_name)
        zipfile.close()
        return response
    account_statment.short_description  = ugettext_lazy('account statment')
    
    def changeform_view(self, request: HttpRequest, object_id: Optional[str], form_url: str, extra_context: Optional[Dict[str, bool]]) -> Any:
        self.fieldsets= self.fieldsets
        transact_to_value = request.COOKIES.get('to_value')
        transact_from_value = request.COOKIES.get('from_value')
        today_full = timezone.now().date()
        extra_context = {
            "filter_label": _('Filter Transactions'), 
            'from' :format_html('<label>{}</label>:  <input type=date value={} id=transactions_from>', _('from'), today_full),
            'to' : format_html(' <label>{}</label>:  <input type=date value={} id=transactions_to>', _('to'), today_full), 
            'trs': [
                _('id of transaction'),
                _('ISSUED AT'),
                _('TRANSACTION TYPE'),
                _('Description'),
                _('debit'),
                _('credit'),
                _('balance'),
                _('VIEW'),
                _('CSV'),
                _('PDF'),
                ],
                "page": _('Page'),
                'of': _('of'),
                'next': _('next'),
                'previous':_('previous'),
                'last': _('last page'),
                'first': _('first')
        }
        supplier = self.get_object(request=request,object_id=object_id, from_field='id')

        if supplier:
            transactions = supplier.transactions.all()

        if transact_to_value and supplier:
            from_date = str_to_date(transact_from_value)
            to_date = str_to_date(transact_to_value)
            transactions = transactions.filter(issued_at__gte=from_date).filter(issued_at__lte=to_date).all()
            # extra_context.update(ConsumerTransaction.prepare_tarnsactions_table(request, transactions, 'admin:payment_supplierpaymenttransaction_change', consumer= 'supplier'))
            extra_context.update(ConsumerTransaction.prepare_tarnsactions_table(request, transactions, 'admin:payment_supplierpaymenttransaction_change', consumer= 'supplier'))
        
        return super().changeform_view(request, object_id=object_id, form_url=form_url,extra_context=extra_context)


    def get_readonly_fields(self, request: HttpRequest, obj: Optional["Supplier"]) -> Union[List[str], Tuple]:
        
        readonly_fields = [
            'id',
            'make_transaction',
            'debit',
            'credit',
            'period_close',
            'get_cash', 
            'get_net',
        ]

        if obj:
          return  readonly_fields + ['cash']

        return [
            'id',
            'credit',
            'period_close',
            'get_cash',
            'debit',
            ]

    def add_view(self, request: HttpRequest, form_url: str='', extra_context: None=None) -> HttpResponse:
        self.fieldsets =  self.add_fieldsets
        response =  super().add_view(request, form_url=form_url, extra_context=extra_context)
        return response                

    def activate(self, request, queryset):
        suppliers_no = queryset.update(is_active=True)
        supplier_string = 'suppliers have' if suppliers_no < 1 else 'client has'
        self.message_user(request, f'{suppliers_no} {supplier_string} activated successfully')
    activate.short_description = ugettext_lazy('Activate selected suppliers')
    
    def export_as_xls(self, request, queryset):
        response    = HttpResponse(content_type='application/vnd.ms-excel')
        xls         = xlsxwriter.Workbook(response)
        work_sheet  = xls.add_worksheet()
        headers_format = xls.add_format()
        headers_format.set_font_shadow()
        headers_format.set_bg_color('gray')
        headers_format.set_border(1)
        headers_format.set_font_color('white')
        headers_format.set_bold()
        headers_format.set_align('center')
        headers_format.set_locked(True)
        headers_format.set_size(15)
        data_format = xls.add_format()
        data_format.set_align('center')
        data_format.set_bg_color('#8d8894')
        data_format.set_font_color('#e7e7e7')
        data_format.set_font_size(14)
        data_format.set_bold()
        data_format.set_border()
        data_format.set_border_color('black')
        sheet_headers  = [
            _('city'),
            _('address'),
            _('phone'),
            _('email'),
            _('id'),
            _('name'),
            ]
        qs_values = queryset.order_by('-id').all()
        make_xls_headers(work_sheet, sheet_headers, headers_format)
        data_fields_names  = [
        'name',
        'id',
        'email',
        'phone',
        'address',
        'city',
        ]
        make_xls_data(work_sheet, qs_values, data_fields_names, data_format)
        xls.close()
        
        return response
    export_as_xls.short_description = ugettext_lazy("Export Selected as xls")


    def deactivate(self, request, queryset):
        suppliers_no = queryset.update(is_active=False)
        supplier_string = 'clients have' if suppliers_no < 1 else 'client has'
        self.message_user(request, f'{suppliers_no} {supplier_string} activated successfully')
    deactivate.short_description = ugettext_lazy('Deactivate selected suppliers')

    def export_invoices_for(self, request, queryset):
        response    = HttpResponse(content_type='application/vnd.ms-excel')
        xls_sheet  =  xlsxwriter.Workbook(response)
       
        headers_format = xls_sheet.add_format()
        headers_format.set_font_shadow()
        headers_format.set_bg_color('gray')
        headers_format.set_border(1)
        headers_format.set_font_color('white')
        headers_format.set_bold()
        headers_format.set_align('center')
        headers_format.set_locked(True)
        headers_format.set_size(15)
        data_format = xls_sheet.add_format()
        data_format.set_align('center')
        data_format.set_bg_color('#8d8894')
        data_format.set_font_color('#e7e7e7')
        data_format.set_font_size(14)
        data_format.set_bold()
        data_format.set_border()
        data_format.set_border_color('black')

        suppliers = queryset.all()
        for supplier in suppliers:
            qs_values = supplier.transactions.order_by('-id').all()
            work_sheet = xls_sheet.add_worksheet()
            make_xls_headers(work_sheet, [
            _('issued_at'),
            _('type_tranasction'),
            _('amount'),
            _('description'),
            _('id'),
            _('supplier'),
            ], headers_format)
            data_fields_names  = [
            'supplier',
            'id',
            'description',
            'amount',
            'type_tranasction',
            'issued_at',
            ]

            make_xls_data(work_sheet, qs_values, data_fields_names, data_format)
        
        xls_sheet.close()
        return response
    export_invoices_for.short_description = ugettext_lazy("Export invoices for ")
    
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset        = super().get_queryset(request)
        supplier_id     =  request.COOKIES.get('supplier_id')
       
        if supplier_id:
            queryset    = queryset.filter(id=supplier_id)
        
        return queryset

    def get_urls(self) -> List[URLPattern]:
        urls =  super().get_urls()
        urls+=[
            path('<int:supplier_id>/make_a_transaction', self.process_withdraw),
            path('<int:supplier_id>/change/<int:id>/download/csv', self.download_transaction_csv , ),
            path('<int:supplier_id>/change/<int:id>/download/pdf', self.download_transaction_pdf , ),
            path('<int:supplier_id>/change/period_close', self.period_close_controller , name='supplier_period_close'),
            path('account-statment/<str:date_from>/<str:date_to>/<str:supplier_id>', self.account_statment_handler , name='supplier_account_statment'),
        ]
        return urls
    
    def account_statment_handler(self, request, date_from, date_to, supplier_id):
        supplier = self.get_object(request, supplier_id)
        return CommonMethods.account_statment_pdf(
            date_from=date_from,
            date_to=date_to,
            consumer_obj=supplier,
            request=request
            )
        
    def period_close_controller(self, request, supplier_id):
        supplier    = self.get_object(request, supplier_id)
        transactions = supplier.transactions
        return CommonMethods.make_peroid_close(transactions, supplier)

      
    def download_transaction_pdf(self, request, **kwargs):
        transaction = SupplierPaymentTransaction.objects.get(id=kwargs['id'])
        return admin_supplier_download_transaction_pdf(transaction, request)

    def download_transaction_csv(self, *args_, **kwargs):
        url = reverse('admin:supplier_transaction_download_csv', args=[kwargs['id']])
        return HttpResponseRedirect(url)

    def save_model(self, request: Any, supplier: "Supplier", form: Any, change: Any) -> None:
        super().save_model(request, supplier, form, change)
        if (not supplier.cash == 0) and (change == False):
            if not SupplierPaymentTransaction.objects.filter(supplier_id=supplier.pk).exists():
                if supplier.cash < 0:
                    try:
                         type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
                    except PaymentTransactionType.DoesNotExist:
                        type_tranasction = PaymentTransactionType.objects.create(
                        name=_('Opening account'),
                        transaction_for=2
                    )
                    SupplierPaymentTransaction.objects.create(
                        amount=abs(supplier.cash),
                        supplier=supplier,
                        type_tranasction=type_tranasction,
                        payment_type=2,
                        issued_by = request.user
                        
                    )
                    return
                try:
                    type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
                except PaymentTransactionType.DoesNotExist:
                    type_tranasction = PaymentTransactionType.objects.create(
                        name=_('Opening account'),
                        transaction_for=1
                    )

            SupplierPaymentTransaction.objects.create(
                amount=supplier.cash,
                supplier=supplier,
                type_tranasction=type_tranasction,
                payment_type=1,
                issued_by = request.user
            )

            
            
    
    def process_withdraw(self, request, supplier_id):
        url = reverse("admin:payment_supplierpaymenttransaction_add")
        url = url + f'supplier/{supplier_id}'
        response = HttpResponseRedirect(url)

        return response
 
    list_per_page = 15
    ordering = ['-id']
    
    class Meta:
        model =  Supplier


admin.site.register(Supplier, SupplierAdmin)