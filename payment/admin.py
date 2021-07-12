from payment.filter import ClientTransactionType, SupplierTransactionType
from typing import (Any, Dict, List, Optional, Sequence)
from django.contrib import admin
from django.contrib.admin.options import (ModelAdmin, TabularInline)
from django.db.models.query import QuerySet
from django.http import request
from django.http.response import (
    HttpResponse, HttpResponseRedirect, JsonResponse)
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls.base import reverse
from django.urls.conf import path
from django.urls.resolvers import URLPattern
from xhtml2pdf import pisa
from payment.models import (Payment, PaymentTransactionType,
                            SupplierPaymentTransaction, ClientPaymentTransaction)
from django.utils.translation import gettext_lazy, ugettext as _, ugettext_lazy
from _helpers.admin import (
    Amount, CommonMethods, ConsumerTransactionDownloder, admin_client_download_transaction_pdf, admin_supplier_download_transaction_pdf, make_xls_data, make_xls_headers, str_to_date)
from _helpers.models import (
    get_currency, get_payment_type, modified_num2words)
from supplier.models import Supplier
from django.contrib import messages
# from django.contrib.humanize.templatetags.humanize import naturalday
import xlsxwriter
from _helpers.admin import PaymentTransactionHelper

from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
import os, sys 
# import win32print

class CannotDelete(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None) -> bool:
        return False


class ViewOnly(CannotDelete):

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False


class PaymentAdmin(ViewOnly):
    search_fields = [
        'id'
    ]


class PaymentTransaction(ViewOnly):
    fields = [
        ('payment_type', 'type_tranasction', 'file_transaction'),
        'description',
    ]


class PaymentTransactionTypeAdmin(admin.ModelAdmin):
    search_fields = [
        'name'
    ]

    ordering = ['-id']

    def lookup_allowed(self, lookup: str, value: str) -> bool:
        print(value)
        lookup_allowed = super().lookup_allowed(lookup, value)
        return lookup_allowed

    def has_delete_permission(self, request: request.HttpRequest, obj: Optional['PaymentTransactionTypeAdmin'] = None) -> bool:
        return False

    def get_queryset(self, request: request.HttpRequest) -> QuerySet:
        transaction_type = request.COOKIES.get('transaction_type_query')
        for_supplier = request.COOKIES.get('for_supplier')
        for_client = request.COOKIES.get('for_client')
        
        return super().get_queryset(request).filter(
            transaction_for=transaction_type, 
            for_supplier=for_supplier,
            for_client=for_client
            )


class ItemsInline(TabularInline):
    class Meta:
        vernose_name = _("transaction details")
        verbose_name_plural = _("transaction details")

    class Media:
        js = ('supplier_dynamic_prices.js',)

    model = SupplierPaymentTransaction.items.through
    extra = 1
    fields = [
        'item',
        'quantity',
        'supplier_price',
        'discount',
        'cost_per_item_supplier',
    ]

    autocomplete_fields = [
        'item'
    ]

    readonly_fields = [
        'cost_per_item_supplier',
    ]

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return super().has_delete_permission(*args, **kwargs)

    can_delete = False


class SupplierPaymentTransactionAdmin(PaymentTransaction):
    class Media:
        js = (
            'supplier_transaction_toggle.js',
            # 'dynamic_supplier_cash.js',
            'amount_str.js',
            'export_daily_reports.js',
        )

    list_display = [
        'id',
        'supplier',
        'parsed_amount',
        'issued_at',
        'type_tranasction'
    ]
    
    actions = [
        'export_as_xls',
    ]
    ordering = ['-id']
    readonly_fields = ['id', 'supplier_cash_html',
                       'supplier_cash_after_transaction', 'issued_at', 'issued_at_int','str_amount', 'issued_by']
    list_filter = (
        'amount', 
        'payment_type', 
        'currency', 
        SupplierTransactionType, 
        )
    search_fields = ('supplier__name', 'supplier__email')
    autocomplete_fields = ['supplier', 'type_tranasction']
    list_per_page = 20
    change_list_template = 'admin/payment/supplierpaymenttransaction/custom_change_list.html'
    change_form_template = 'admin/payment/supplierpaymenttransaction/custom_change_form.html'
    empty_value_display = 0
    def add_view(self, request, form_url="", extra_context=None):
        transaction_type = request.COOKIES.get('value_transaction_supplier')
        suppliers_url = reverse('admin:supplier_supplier_changelist')
        suppliers_url = request.build_absolute_uri(suppliers_url)
        response = super().add_view(request, form_url=form_url, extra_context=extra_context)
        if not transaction_type:
            transaction_type = 1

        response.set_cookie('for_client', False)
        response.set_cookie('transaction_type_query', transaction_type)
        response.set_cookie('for_supplier', True)
        return response

    def changelist_view(self, request: request.HttpRequest, extra_context: Optional[Dict[str, str]] = None) -> TemplateResponse:
        extra_context = {'label': _(
            'Daily transactions'), 'btn_label': _("Export")}
        response = super().changelist_view(request, extra_context=extra_context)

        return response

    def amount_currency_html(self, obj):
        return obj.amount_currency()
    amount_currency_html.short_description = _('amount')

    def export_as_xls(self, request, queryset):
        return CommonMethods.export_as_xls(request, queryset)
    export_as_xls.short_description = ugettext_lazy("Export Selected")

    def get_supplier_name(self, request, name):
        supplier = Supplier.objects.filter(name=name)
        if supplier.exists():
            supplier = supplier.get()
            return JsonResponse(
                {
                    'cash_html': supplier.get_cash(),
                    'cash': supplier.prepare_net(),
                }
            )
        return JsonResponse(data={})

    def get_fields(self, request, obj=None):
        old_fields = super().get_fields(request, obj) + [
            ('supplier',), 
            'supplier_cash_html'
            , 
        ]

        if not obj:
             return [old_fields[0]] + ['amount', 'str_amount'] +old_fields[1:]+ ['supplier_cash_after_transaction', ]
        return [
        ('amount_currency', 'str_amount') , 'issued_by'] + old_fields + ['print_transaction', 'issued_at_int']

        
    def save_model(self, request, obj, form, change) -> None:
        if obj.payment_type == 2:
            obj.supplier.cash = abs(obj.supplier.cash - obj.amount)
        else:
            obj.supplier.cash = abs(obj.supplier.cash) + obj.amount
        obj.supplier.save()
        obj.issued_by =  request.user
        return super().save_model(request, obj, form, change)

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        urls += [
            path('supplier/<str:name>', self.get_supplier_name,
                 name='get_supplier_name'),
            path('add/supplier/<int:supplier_id>',
                 self.filtered_queryset, name='filtered_queryset'),
            path('<int:id>/download', self.download_transcation,
                 name='supplier_transaction_download_csv'),
            path('export_daily_reports', self.export_daily_reports,
                 name='supplier_export_daily_reports'),
            path('amount_to_string', self.amount_to_string,
                 name='supplier_amount_to_string'),
            path('<int:pk>/print_transaction', self.print_transaction_handler,
                 name='supplier_print_transaction'),
        ]
        return urls

    def print_transaction_handler(self, request, pk):
        transaction = self.get_object(request, pk)
        return admin_supplier_download_transaction_pdf(transaction, request)

    def filtered_queryset(self, request, supplier_id):
        response = self.add_view(request=request, extra_context={
                                 'queryset': self.get_queryset(request).filter(id=1)})
        response.set_cookie('supplier_id', supplier_id)
        return response

    def amount_to_string(self, request):
        amount = float(request.POST.get('amount', 0))

        delemiter = ' '
        if amount < 0:
            amount = abs(amount)
            delemiter = _('credit')

        amount = modified_num2words(amount)
        response = JsonResponse({'str': delemiter+' ' + amount})
        response.status_code = 200
        return response

    def export_daily_reports(self, request, **kwargs):
        export_reports_date = request.COOKIES.get('export_reports_for')

        if not export_reports_date:
            return HttpResponseRedirect('./')

        export_reports_date = str_to_date(export_reports_date)

        transactions = SupplierPaymentTransaction.objects.filter(
            issued_at__contains=export_reports_date)
        if not transactions.exists():
            # messages.add_message(request, messages.ERROR, _('There are no transactions for that date'))
            return HttpResponse(_('There are no transactions for that date'))

        return CommonMethods.generate_daily_tranasctions(transactions,consumer='supplier')


    def download_transcation(self, request, **kwargs):
        transaction =  self.get_object(request, kwargs['id'])
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

        make_xls_data(work_sheet, [transaction], data_fields_names, data_format)
        
        xls_sheet.close()
        return response

class ClientPaymentTransactionAdmin(PaymentTransaction):
    class Media:
        js = (
            'export_daily_reports.js',
            'amount_str.js',
            'client_transaction_toggle.js',
        )

    list_display = [
        'id', 
        'client', 
        'parsed_amount', 
        'issued_at', 
        'type_tranasction'
    ]
    empty_value_display = 0

    ordering = [
        'id', 
        ]
    
    readonly_fields = [
        'id',
        'issued_at_int',
        'client_cash_html',
        'client_cash_after_transaction',
        'amount_currency',
        'send_to_printer',
        'str_amount',
        'issued_by'
    ]

    list_filter = (
        'issued_at',
        'payment_type',
        'amount',
        'issued_by',
        ClientTransactionType,
    )
                   
    search_fields = (
        'client__name', 
        'client__email'
    )

    list_per_page = 20

    change_list_template = 'admin/payment/clientpaymenttransaction/custom_change_list.html'
    change_form_template = 'admin/payment/clientpaymenttransaction/custom_change_form.html'

    autocomplete_fields = ['client', 'type_tranasction']

    def get_fields(self, request, obj=None):
        old_fields = super().get_fields(request, obj) + [
            ('client', ), 
            'client_cash_html', ]
        if not obj:
            return [old_fields[0]] + ['amount', 'str_amount'] +old_fields[1:] +['client_cash_after_transaction',]
        return [
            ('amount_currency', 'str_amount'),'issued_by'] + old_fields + ['print_transaction', 'issued_at_int']

    def get_client_name(self, request, name):
        from client.models import Client

        client = Client.objects.filter(name=name)
        if client.exists():
            client = client.get()
            return JsonResponse(
                {
                    'cash_html': client.get_cash(),
                    'cash': client.prepare_net(),
                }
            )
        return JsonResponse({"status_code": 404})

    def print_transaction_handler(self, request, pk):
        transaction = self.get_object(request, pk)
        return admin_client_download_transaction_pdf(transaction, request)

    def changelist_view(self, request: request.HttpRequest, extra_context: Optional[Dict[str, str]] = None) -> TemplateResponse:
        extra_context = {'label': _(
            'Daily transactions'), 'btn_label': _("Export")}
        return super().changelist_view(request, extra_context=extra_context)

    actions = ['export_as_xls']

    def export_as_xls(self, request, queryset):
       return CommonMethods.export_as_xls(request, queryset, 'client')
    export_as_xls.short_description = ugettext_lazy("Export Selected")

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        urls += [
            path('client/<str:name>', self.get_client_name,
                 name='get_client_name'),
            path('<int:id>/download', self.download_transcation,
                 name='client_transaction_download_csv'),
            path('export_daily_reports', self.export_daily_reports,
                 name='client_export_daily_reports'),
            path('amount_to_string', self.amount_to_string,
                 name='amount_to_string'),
            path('<int:pk>/print_transaction', self.print_transaction_handler,
                 name='client_print_transaction'),
        ]
        return urls

    def amount_to_string(self, request):
        delemiter = ' '
        amount = float(request.POST.get('amount', 0))
        if amount < 0:
            amount = abs(amount)
            delemiter = _('credit')

        amount = modified_num2words(amount)
        response = JsonResponse({'str': delemiter+' ' + amount})
        response.status_code = 200
        return response

    def transaction_url(self, request, transaction_id):
        return reverse('admin:payment_clientpaymenttransaction_change', args=[transaction_id])
       
    def export_daily_reports(self, request, **kwargs):
        export_reports_date = request.COOKIES.get('export_reports_for')
        if not export_reports_date:
            return HttpResponseRedirect('./')

        export_reports_date = str_to_date(export_reports_date)

        transactions = ClientPaymentTransaction.objects.filter(
            issued_at__contains=export_reports_date)

        if not transactions.exists():
            return HttpResponse(_('There are no transactions for that date'))

        return CommonMethods.generate_daily_tranasctions(transactions,'client')
    export_daily_reports.short_description = _('export daily transactions')

    def download_transcation(self, request, **kwargs):
        transaction =  self.get_object(request, kwargs['id'])
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
        work_sheet = xls_sheet.add_worksheet()
        make_xls_headers(work_sheet, [
            _('issued_at'),
            _('type_tranasction'),
            _('amount'),
            _('description'),
            _('id'),
            _('client'),
            ], headers_format)
        data_fields_names  = [
            'client',
            'id',
            'description',
            'amount',
            'type_tranasction',
            'issued_at',
            ]

        make_xls_data(work_sheet, [transaction], data_fields_names, data_format)
        
        xls_sheet.close()
        return response


    def add_view(self, request, form_url="", extra_context=None):
        transaction_type = request.COOKIES.get('value_transaction_client')
        clients_url = reverse('admin:client_client_changelist')
        clients_url = request.build_absolute_uri(clients_url)
        response = super().add_view(request, form_url=form_url, extra_context=extra_context)
        print(request.COOKIES)
        print(request.META['HTTP_REFERER'])


        if not transaction_type:
            transaction_type = 1
        
        
        response.set_cookie('transaction_type_query', transaction_type)
        response.set_cookie('for_supplier', False)
        response.set_cookie('for_client', True)
        return response

    def save_model(self, request, obj, form, change) -> None:
        if obj.payment_type == 2:
            obj.client.cash = abs(obj.client.cash - obj.amount)
        else:
            obj.client.cash = abs(obj.client.cash) + obj.amount
        obj.client.save()
        obj.issued_by =  request.user
        return super().save_model(request, obj, form, change)

    def get_list_filter(self, request: request.HttpRequest) -> Sequence[str]:
        filters = super().get_list_filter(request=request)
        print(filters)
        return filters
        
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentTransactionType, PaymentTransactionTypeAdmin)
admin.site.register(ClientPaymentTransaction, ClientPaymentTransactionAdmin)
admin.site.register(SupplierPaymentTransaction,SupplierPaymentTransactionAdmin)
