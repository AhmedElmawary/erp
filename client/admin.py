import os

from django.template.response import TemplateResponse
from _helpers.common import make_list_of_lists
from app_user.models import ClosingPeriod
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.template.loader import render_to_string
from num2words import num2words
from xhtml2pdf import pisa
from _helpers.models import areas_ar_en, find_in, get_currency, get_payment_type, modified_num2words
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
from django.http.request import HttpHeaders, HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse
from django.urls.conf import path
from django.urls.resolvers import URLPattern
from django.utils.html import format_html
from payment.models import ClientPaymentTransaction, PaymentTransactionType
from django.contrib import admin
from .models import Client
from django.utils.translation import gettext, ugettext as _, ugettext_lazy 
import xlsxwriter
from _helpers.admin import Amount, ClientHelper, CommonMethods, ConsumerTransaction,ConsumerTransactionDownloder, admin_client_download_transaction_pdf, admin_supplier_download_transaction_pdf, make_xls_data, make_xls_headers, str_to_date
from zipfile import ZipFile

class ClientAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'client_transactions.js',
            'client_account_statment.js'
            )
        css = {
            "all":('client_admin.css',)
        }

    model = Client
    search_fields = ['name', 'phone', 'email']
    extra = 1
    list_display_links = [
        'name'
    ]
    list_display = [
    'id',
    'name',
    'phone',
    'is_active',
    'taxes',
    # 'make_transaction',
    'parsed_get_debit',
    'parsed_get_credit',
    'parsed_get_net',
    'account_statment_from',
    'account_statment_to',
    'account_statment_btn',
    ]

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
                _('cash')
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

    search_fields = ['name', 'phone', 'email','area__name', 'city']
    list_filter = ('is_active', 'taxes')
    list_per_page = 20
    actions = [
        _('activate'),
        _('deactivate'),
        _('export_as_xls'),
        _('export_invoices_for'),
    ]
    
    change_form_template  = 'admin/client/client/custom_change_form.html'
    change_list_template = 'admin/client/client/custom_change_list.html'

    def activate(self, request, queryset):
        client_no = queryset.update(is_active=True)
        supplier_string = 'clients have' if client_no < 1 else 'client has'
        self.message_user(request, f'{client_no} {supplier_string} activated successfully')
    activate.short_description = ugettext_lazy('Activate selected clients')
    

    def deactivate(self, request, queryset):
        client_no = queryset.update(is_active=False)
        supplier_string = 'clients have' if client_no < 1 else 'client has'
        self.message_user(request, f'{client_no} {supplier_string} activated successfully')
    deactivate.short_description = ugettext_lazy('Deactivate selected clinets')

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

        clients = queryset.all()
        for supplier in clients:
            qs_values = supplier.transactions.order_by('-id').all()
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

            make_xls_data(work_sheet, qs_values, data_fields_names, data_format)
        
        xls_sheet.close()
        return response
    export_invoices_for.short_description = ugettext_lazy('Export invoices for')


    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> Tuple[QuerySet, bool]:
        area = find_in(areas_ar_en(), search_term)
        if area:
            search_term = area[search_term]
        return super().get_search_results(request, queryset, search_term)

    def get_readonly_fields(self, request: HttpRequest, obj: Optional["Client"]) -> Union[List[str], Tuple]:
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
             return readonly_fields+ ['cash']

        return readonly_fields 

        
    def add_view(self, *args, **kwargs):
        self.fieldsets = self.add_fieldsets
        return super().add_view(*args, **kwargs)

    def changeform_view(self, request: HttpRequest, object_id: Optional[str], form_url: str, extra_context: Optional[Dict[str, bool]]) -> Any:
        transact_to_value = request.COOKIES.get('to_value')
        transact_from_value = request.COOKIES.get('from_value')
        today_full = datetime.today().date()
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

        client = self.get_object(request=request,object_id=object_id)
        
        if not client:
            return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)
        
        transactions = client.transactions.all()

        if transact_to_value:
            to_date=str_to_date(transact_to_value)
            from_date=str_to_date(transact_from_value)
            transactions = transactions.filter(issued_at__gte=from_date).filter(issued_at__lte=to_date).all()

        extra_context.update(ConsumerTransaction.prepare_tarnsactions_table(request, transactions, 'admin:payment_clientpaymenttransaction_change', consumer= 'client'))
        return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        urls += [
            path('<int:client_id>/make_a_transaction', self.process_make_transaction, ),
            path('<int:client_id>/change/<int:id>/download/csv', self.download_transaction_csv ,),
            path('<int:client_id>/change/<int:id>/download/pdf', self.download_transaction_pdf , name='client_transaction_download_pdf'),
            path('<int:client_id>/change/period_close', self.period_close_controller , name='client_period_close'),
            path('account-statment/<str:date_from>/<str:date_to>/<str:client_id>', self.account_statment_handler , name='client_account_statment'),
        ]
        return urls

    def account_statment_handler(self, request, date_from, date_to, client_id):
        client = self.get_object(request, client_id)
        
        return CommonMethods.account_statment_pdf(
            date_from=date_from,
            date_to=date_to,
            consumer_obj=client,
            request=request
        )
    
    def period_close_controller(self, request, client_id):
        client    = self.get_object(request, client_id)
        transactions = client.transactions
        return CommonMethods.make_peroid_close(transactions, client)



    def changelist_view(self, request: HttpRequest, extra_context: Optional[Dict[str, str]]=None) -> TemplateResponse:
        extra_context = {
            'to': _('to'),
            'from': _('from'),
            'export': _('export'),
            "account_stament_label": _('account statment')
        }

        response  = super().changelist_view(request, extra_context=extra_context)
        if request.COOKIES.get('client_id'):
            response.delete_cookie('client_id')

        return response



    def process_make_transaction(self, request, **kwargs):
        url = reverse("admin:payment_clientpaymenttransaction_add")
        response = HttpResponseRedirect(url)
        response.set_cookie('client_id', kwargs.get('client_id'))
        return response

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        client_id   =  request.COOKIES.get('client_id')

        if not client_id:
            return super().get_queryset(request)
        client_list_path = reverse('admin:client_client_changelist')    
        queryset = super().get_queryset(request)

        if  not request.path == client_list_path:
            queryset = queryset.filter(id=client_id)

        return queryset



    def download_transaction_pdf(self, request, **kwargs):
        transaction = ClientPaymentTransaction.objects.get(id=kwargs['id'])
        return admin_client_download_transaction_pdf(transaction, request)

         

    def download_transaction_csv(self, *args_, **kwargs):
        url = reverse('admin:client_transaction_download_csv', args=[kwargs['id']])
        return HttpResponseRedirect(url)

    def has_delete_permission(self, request, obj=None):
        return False

    def activate_clients(self, request, queryset):
        clinets_no = queryset.update(is_active=True)
        client_string = 'clients have' if clinets_no < 1 else 'client has'
        self.message_user(request, f'{clinets_no} {client_string} activated successfully')

    def dactivate_clients(self, request, queryset):
        clinets_no = queryset.update(is_active=False)
        client_string = 'clients have' if clinets_no < 1 else 'client has'
        self.message_user(request, f'{clinets_no} {client_string} deactivated successfully')


    
    def get_action(self, action: Union[Callable, str]) -> Tuple[Callable, str, str]:
        return super().get_action(action)
    
    
    def save_model(self, request: Any, client: "Client", form: Any, change: Any) -> None:
        super().save_model(request, client, form, change)
        if (not client.cash == 0) and (change == False):
            if not ClientPaymentTransaction.objects.filter(client_id=client.pk).exists():
                if client.cash < 0:
                    try:
                        type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
                    except PaymentTransactionType.DoesNotExist:
                        type_tranasction = PaymentTransactionType.objects.create(
                        name=_('Opening account'),
                        transaction_for=2,
                    )

                    ClientPaymentTransaction.objects.create(
                    amount=abs(client.cash),
                    client=client,
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
                    transaction_for=1,
                )

                ClientPaymentTransaction.objects.create(
                amount=client.cash,
                client=client,
                type_tranasction=type_tranasction,
                payment_type=1,
                issued_by = request.user
            )



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


admin.site.register(Client, ClientAdmin)
