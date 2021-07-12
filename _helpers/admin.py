import abc
from app_user.models import ClosingPeriod
from datetime import datetime
from django.db.models import Q

from django.core.validators import int_list_validator
from libreries.num2words.num2words import num2words
from typing import Dict, List, Optional
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.html import format_html, linebreaks
from django.utils.translation import gettext as _, ugettext_lazy
from _helpers.models import (CURRENCIES, PAYMENTTYPES,  get_currency, get_payment_type, modified_num2words)
import csv
from django.http import HttpResponse
import xlsxwriter
from django.utils import timezone
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.paginator import Paginator
import shutil
import math
import os
from django.conf import settings
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
 

def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    
    values = []
    for obj in queryset:
        for field in field_names:
            value = getattr(obj, field)
            if field == 'payment_type':
                value = get_payment_type(getattr(obj, field)) 
            if field == 'paymenttransaction_ptr':
                continue

            values.append(value)
        writer.writerow(values)

    return response

# interface of ReadOnly
class ReadOnlyContract():
    def has_change_permission(self, request: HttpRequest, obj: Optional[ModelAdmin]) -> bool:
        pass
    
    def has_delete_permission(self, request: HttpRequest, obj: Optional[ModelAdmin]) -> bool:
        pass

class ReadOnlyImplemented(ReadOnlyContract):
    def has_change_permission(self, request: HttpRequest, obj: Optional[ModelAdmin]) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[ModelAdmin]) -> bool:
        return False

class ReadOnlyAdmin(admin.ModelAdmin, ReadOnlyImplemented):
    pass

class CSVContract(abc.ABC):
    pass


class ConsumerTransaction:
    @classmethod
    def prepare_tarnsactions_table(cls, request, transactions, view_str_link,consumer):
        pdf_icon = format_html('<img src="https://img.icons8.com/offices/30/000000/pdf.png"/>')
        view_icon = format_html('<img src="https://img.icons8.com/metro/26/000000/visible.png"/>')
        csv_icon = format_html('<img src="https://img.icons8.com/officel/35/000000/export-csv.png"/>')
        values = [ ]

        balance=0
        for trasaction in transactions.order_by('id'):
            transaction_dict = {}
            debit = '-'
            credit = '-'
            if trasaction.type_tranasction.transaction_for == 1:
                debit = trasaction.amount
                balance += debit
            else:
                credit = trasaction.amount
                balance -= credit 

            transaction_dict['id'] = trasaction.pk
            transaction_dict['issued at'] = trasaction.issued_at
            transaction_dict['type_tranasction'] =  get_payment_type(trasaction.payment_type)
            transaction_dict['description'] = '-' if not str(trasaction.type_tranasction) else  str(trasaction.type_tranasction)
            transaction_dict['description'] += ' ' if not trasaction.description else  trasaction.description
            transaction_dict['debit']  = debit
            transaction_dict['credit']  = credit
            transaction_dict['balance'] = balance
            transaction_dict['view'] = format_html("<a href='{}'> {} </a>", reverse(view_str_link, args=[transaction_dict['id']]),  view_icon)
            transaction_dict['Downloas as csv'] = format_html("<a href='{}'> {} </a>",f'{transaction_dict["id"]}/download/csv', csv_icon)
            transaction_dict['download as pdf'] = format_html('<a href="{}"> {} </a>',f'{transaction_dict["id"]}/download/pdf', pdf_icon)
            values.append(transaction_dict.values())
        
        transactions_paginator = Paginator(object_list=values, per_page=15)
        page_obj = transactions_paginator.get_page(request.GET.get('page'))

        return {'page_obj':page_obj,"transactions_lable": _("Transactions") , }

    @classmethod
    def _assign_values(cls, data, values):
            pass

    @classmethod
    def _del_from_trasaction_key(cls, transaction, key):
            if transaction.get(key):
                del transaction[key]    


class Supplier:
    headers_len = 0
    rows_number_per_sheet = 0

    @classmethod
    def transactions_csv(cls, admin_instance, request, queryset):
        suppliers = queryset.all()
        response = HttpResponse()
        response['Content-Type'] = 'application/csv'
        response['Content-Disposition'] = f'attachment; filename=invoices.csv'
        document = csv.writer(response)
        cols = ['name', 'registed at' , 'invoice no', 'invoice type', 'amount', 'currency','description', 'issued at']
        document.writerow(cols)
        for supplier in suppliers:
            transactions = supplier.transactions.all()
            for row in transactions:
                document.writerow([
                    supplier.name,
                    str(supplier.created_at),
                    row.id,PAYMENTTYPES[row.payment_type-1][-1],
                    row.amount, CURRENCIES[row.currency -1 ][-1],
                    row.description,
                    row.issued_at
                ])

        return response

    @classmethod
    def transactions_xls(cls, request, queryset, admin_instance = None):
        response = HttpResponse(content_type='application/xls')
        response['Content-Disposition'] = f'attachment; filename=invoices_{timezone.now().date()}-{timezone.now().time()}.xls'

        document  =  xlsxwriter.Workbook(response)

        cols = [
            _('name'),
            _('registered at' ),
            _('invoice no'),
            _('invoice type'),
            _('amount'),
            _('currency'),
            _('description'),
            _('issued at')
            ]

        suppliers = queryset.all()
        for supplier in suppliers:
            sheet = document.add_worksheet(str(supplier))
            cls._writer_headers_xls(cols, sheet)
            cls._write_data_xls(supplier, sheet)

        document.close()


        return response

    @classmethod
    def _set_document_len(cls, headers):
        cls.headers_len = len(headers)
    
    @classmethod
    def _writer_headers_xls(cls, headers, sheet) -> None:
        cls._set_document_len(headers)
        for col in range(cls.headers_len):
            sheet.write(0, col, headers[col])
    
    @classmethod
    def _write_data_xls(cls, supplier, sheet) -> None:
        data = cls._preapre_data_xls(supplier)
        for row in range(1, cls.rows_number_per_sheet+1):
            for col in range(cls.headers_len):
                sheet.write(row, col, data[row-1][col])

    @classmethod
    def _preapre_data_xls(cls, supplier):
        internal_data =  []
        data = []
        transactions = supplier.transactions.all()
        for transaction in transactions:
            internal_data.append(str(supplier))
            internal_data.append(str(supplier.created_at))
            internal_data.append(transaction.id)
            internal_data.append(str(PAYMENTTYPES[transaction.payment_type-1][-1]))
            internal_data.append(transaction.amount)
            internal_data.append(str(CURRENCIES[transaction.currency -1 ][-1]))
            internal_data.append(transaction.description)
            internal_data.append(str(transaction.issued_at))
            data.append(internal_data)
            internal_data =  []

        cls._rows_number_per_sheet(data)
        return data
    
    @classmethod
    def _rows_number_per_sheet(cls, data):
        cls.rows_number_per_sheet = len(data)

    @classmethod
    def account_statment_csv(cls, data):
        response  = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        cols = [_('description'), _('id'), _('issued at'),  _('transaction amount'), _('transaction detail'), _('transaction type'),_('credit'), _('debit'), _('balance') ]
        values = []

        for transaction in data:
            cash = transaction.supplier.cash if transaction.supplier.cash else transaction.supplier.debit - transaction.supplier.credit
            values.append([transaction.description, transaction.id, transaction.issued_at, transaction.amount,str(transaction.type_tranasction), PAYMENTTYPES[transaction.payment_type - 1][-1],transaction.supplier.credit, transaction.supplier.debit, cash])

        writer.writerow(cols)
        writer.writerows(values)
        

        return response

    @classmethod
    def account_statment_pdf(cls, suppliers):
        suppliers = cls._get_data(suppliers)
        cols = [
        _('Blanace'),
        _('Credit'),
        _('Debit'),
        _("Issued at"),
        _("Id"),
        _('Description'),
        ]
        context = {
            'cols': cols,
            'branch_label': _('the centeral branch'),            
            'suppliers': suppliers,
            'transactions_label': _('account statment for supplier'),
            'from': _('from'),
            'to': _('to'),
            'print':_('print'),
            'cancel':_('cancel'),
            'total_cost': _('net cost')
            }

        template = render_to_string('supplier/statment/pdf.html', context)
        # response = HttpResponse(content_type='application/pdf')
        response = HttpResponse(content_type='text/html')
        response['Content-Disposition'] = 'inline; filename=Account_Statment.pdf'
        
        # pisa.CreatePDF(
        #     src=template,
        #     dest=response,
        #     encoding='utf-8'
        # ).addPageCount()
        
        return HttpResponse(template)

    @classmethod
    def _parse_supplier_transactions(cls, supplier, date_from=None, date_to=None):
        transactions_list = []
        delimiter = '+'
        net_cash = 0
        transactions_queryset = supplier.transactions
        if date_from:
            transactions_queryset = transactions_queryset.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
        transactions_queryset = transactions_queryset.all()
        if transactions_queryset.exists():
            for transaction in transactions_queryset:
                if transaction.payment_type == 1:
                    debit = transaction.amount
                    credit=0
                    net_cash += transaction.amount
                    delimiter = '+'
                else:
                    delimiter = '-'
                    credit = transaction.amount
                    debit=0
                    net_cash -= transaction.amount

                inner_description = transaction.description if transaction.description else ''
                transactions_list.append(
                [
                    str(net_cash),
                    '- '+  str(credit),
                    '+ '+ str(debit),
                    str(transaction.issued_at),
              #      transaction.id,
                    f'{delimiter} {transaction.type_tranasction} {inner_description}'

                ])
            return transactions_list

    @classmethod
    def _get_data(cls, suppliers):
        all_data = []
        for supplier in suppliers:
            all_data.append(
            {
                'supplier':supplier,
                'transactions_list':cls._parse_supplier_transactions(supplier)
            }
            )
        return all_data
    
    @classmethod
    def new_account_statment_pdf(cls, supplier, date_from=None, date_to=None):
        supplier_name = str(supplier)
        data = []
        total = 0
        supplier_transactions = supplier.transactions.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
       
        total_transaction_count  = math.ceil(supplier_transactions.count()  / 25)
       
        cols = [
                [
                    'debit',
                    _('Debit'),
                ],
                [
                    'credit',
                    _('Credit'),
                ], 
                [
                    'description',
                    _('Description'),
                ],
                [
                    'transaction',
                    _('transaction type'),
                ],
                [
                    'issued',
                    _('transaction date'),
                ],
                [
                        'id_transaction',
                        _('id of transaction'),
                ],
            ]
        index = 1
        for transaction in supplier_transactions.all():
            credit = '-'
            debit = '-'

            if transaction.payment_type == 1:
                debit = transaction.amount
                total -= debit
            else:
                credit = transaction.amount
                total += credit
            des = str(transaction.type_tranasction)
            des += '' if not transaction.description else ' - '+ transaction.description
            
            data.append([
                Amount.parse(debit) if not debit == '-' else debit,
                Amount.parse(credit) if not credit == '-' else credit,
                des,
                str(get_payment_type(transaction.payment_type)),
                datetime.strftime(transaction.issued_at, '%Y-%m-%d   %I:%M %p'),
                index
            ])
            index+=1
            


        today = timezone.now()

        context = {
            'cols': cols,
            'transactions': data,
            'title': _('account statments to ') +' '+ naturaltime(today),
            'app_name': _('closthes shop el wensh'),
            'phone': '011114548878',
            'account_statment':_('account statment for supplier'),
            'date': today   ,
            'branch': _('Main brnach'),
            'address': _("shubra st"),
            'side_info': _('transactions which have been done till') +' : '+ str(today.date()),
            # 'user': request.user,
            'at_date': today.strftime("%Y-%m-%d") ,
            'at_time': today.strftime("%H:%I") ,
            'accountant': _('accountant'),
            'authorize': _("authorize"),
            'reciver': _('reciver'),
            'total': Amount.parse(total) ,
            'total_str': _('total'),
            'next_page': format_html('<pdf:nextpage>'),
            'total_transaction_count': total_transaction_count,
            'page_number': 1,
            'supplier': supplier_name
        }

        template = render_to_string('supplier/statment/pdf.html', context)
        file_name = 'templates/supplier/statment/output.pdf'
        new_file_name = f'suppliers/{supplier_name}.pdf' 
        result_file = open(file_name, "wb")
        
        pisa.CreatePDF(
            src=template,
            dest=result_file,
            
            encoding='utf-8'
        ).addPageCount()
        
        shutil.copy2(file_name, new_file_name)

        return new_file_name


    @classmethod
    def new_get_data(cls, supplier, date_from=None, date_to=None):
        all_data = []
        all_data.append(
        {
            'supplier':supplier,
            'transactions_list':cls._parse_supplier_transactions(supplier, date_from, date_to)
        }
        )
        return all_data

    @classmethod
    def _get_supplier_transactions(cls, suppliers, date_from=None, date_to=None):
        transations = []
        for supplier in suppliers:
            transactions_queset = supplier.transactions
            if date_from:
                transactions_queset = transactions_queset.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
            transactions_queset = transactions_queset.all()
            for transaction in transactions_queset:
                credit = 0
                debit = 0
                delimiter = '+'
                if transaction.payment_type == 1:  
                    debit = transaction.amount 
                else:
                    delimiter = '-'
                    credit = transaction.amount
                transations.append(
                    [
                        delimiter + str(transaction.amount),
                        credit,
                        '- '+debit,
                        transaction.issued_at+ ' - '+ str(transaction.issued_at) ,
                  #      transaction.id,
                        f'{delimiter} {transaction.type_tranasction} {transaction.description}'
                    ]
                    )
        return transations



def str_to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').strftime('%Y-%m-%d')


class ConsumerTransactionDownloder:
    @classmethod
    def download_csv(self, transaction, fields=None, values=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(str(transaction))
        writer = csv.writer(response)
        writer.writerows([fields, values])
        return response

    @classmethod
    def download_pdfs(cls, transactions, consumer):
        date = str_to_date(datetime.today().strftime('%Y-%m-%d'))
        filename = 'Transactions for {}'.format(date)

        responese = HttpResponse(content_type='application/pdf; charset=UTF-8')
        
        responese['Content-Disposition'] = 'inline; filename={}.pdf'.format(filename)

        context_data = cls._preapare_data_transactions_pdfs(transactions, consumer)
        template = cls._prepare_template(context_data)
        
        # pisa_status = pisa.CreatePDF(
        #     template,
        #     dest=responese,
        #     encoding='UTF-8'
        # )
    
        return HttpResponse(template)

    @classmethod
    def _prepare_template(cls, data,path='payment/transactions/pdf.html'):
        return render_to_string(template_name=path, context=data)
    
    @classmethod
    def _preapare_data_transactions_pdfs(cls, transactions, consumer):
        cols =  [
            _('ID'),
            _('supplier' if consumer == 'supplier'else "Client"), _('AMOUNT'),
            _('PAYMENT TYPE'),
            _('Description'),
            _('ISSUED AT')
        ]
        
        values = []
        CONTENT = []
        for tansaction in transactions:
            des = tansaction.description if tansaction.description else '-'
            des +=tansaction.type_tranasction
            values.append(tansaction.id)
            values.append(str(getattr(tansaction, consumer)))
            values.append( _(get_payment_type(tansaction.payment_type)))
            values.append( _(des))
            values.append(tansaction.issued_at)
            CONTENT.append(values)
            values=[]
        return {
            'values': CONTENT, 
            'cols': cols, 
            'title': 'tansactions',
            'print':_('print'),
            'cancel':_('cancel'),
            }

    @classmethod
    def as_pdf(self, transaction : "TransactionPayment", fields :Dict, values : Dict, request: "HttpRequest",template_path : str='supplier/transaction/pdf.html'):
        response =  HttpResponse(content_type='text/html')
        # response =  HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = f'attachment; filename={str(transaction)}.pdf'
        response['Content-Disposition'] = f'attachment; filename={str(transaction)}.pdf'
        context = {
            'fields': fields,
            'values': values,
            'print':_('print'),
            'cancel':_('cancel'),

        }

        template_rendered_string = render_to_string(template_path, context, request)

        # pisa_status = pisa.CreatePDF(
        #     template_rendered_string, dest=response, encoding='UTF-8'
        # )

        if pisa_status.err:
                return HttpResponse("we faced some issues while porcessing  pdf")
        
        return HttpResponse(template_rendered_string)


class ClientHelper():
    @classmethod
    def _get_data(cls, clients):
        all_data = []
        for client in clients:
            all_data.append(
            {
                'client':client,
                'transactions_list':cls._parse_client_transactions(client)
            }
            )
        return all_data

    @classmethod
    def new_account_statment_pdf(cls, client, date_from=None, date_to=None):
        
        client_name = str(client)
        data = []
        total = 0
        client_transactions = client.transactions.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
        if  client_transactions.exists():
            
            total_transaction_count  = math.ceil(client_transactions.count()  / 25)
       
     
            cols = [
                [
                    'debit',
                    _('Debit'),
                ],
                [
                    'credit',
                    _('Credit'),
                ], 
                [
                    'description',
                    _('Description'),
                ],
                [
                    'transaction',
                    _('transaction type'),
                ],
                [
                    'issued',
                    _('transaction date'),
                ],
                [
                    'id_transaction',
                _('id of transaction'),
                ],
            ]
            index = 1
            for transaction in client_transactions.all():
                credit = '-'
                debit = '-'

                if transaction.payment_type == 1:
                    debit = transaction.amount
                    total += debit
                else:
                    credit = transaction.amount
                    total -= credit
                des = str(transaction.type_tranasction)
                des += '' if not transaction.description else ' - '+ transaction.description
            
            
                data.append([
                    Amount.parse(debit) if not debit == '-' else debit,
                    Amount.parse(credit) if not credit == '-' else credit,
                    des,
                    str(get_payment_type(transaction.payment_type)),
                    datetime.strftime(transaction.issued_at, '%Y-%m-%d   %I:%M %p'),
          #          transaction.id,
                    index
                ])
                index+=1
            


            today = timezone.now()

            context = {
            'cols': cols,
            'transactions': data,
            'title': _('account statments to ') +' '+ naturaltime(today),
            'app_name': _('closthes shop el wensh'),
            'phone': '011114548878',
            'date': today   ,
            'branch': _('Main brnach'),
            'address': _("shubra st"),
            'side_info': _('transactions which have been done between') +' : '+ str(client_transactions.first().issued_at.date()) +' - '+str(client_transactions.last().issued_at.date()),
            # 'user': request.user,
            'at_date': today.strftime("%Y-%m-%d") ,
            'at_time': today.strftime("%H:%I") ,
            'accountant': _('accountant'),
            'authorize': _("authorize"),
            'account_statment':_('account statment for client'),
            'reciver': _('reciver'),
            'total': Amount.parse_with_label(total) ,
            'total_str': _('total'),
            'next_page': format_html('<pdf:nextpage>'),
            'total_transaction_count': total_transaction_count,
            'page_number': 1,
            'client': client_name
        }

            template = render_to_string('client/statment/pdf.html', context)
            file_name = 'templates/client/statment/output.pdf'
            new_file_name = f'clients/{client_name}.pdf' 
            result_file = open(file_name, "wb")
            
            pisa.CreatePDF(
                src=template,
                dest=result_file,
                
                encoding='utf-8'
            ).addPageCount()
            
            shutil.copy2(file_name, new_file_name)
    
            return new_file_name
    
        
    @classmethod
    def new_get_data(cls, client, date_from=None, date_to=None):
        all_data = []
        all_data.append(
        {
            'client':client,
            'transactions_list':cls._parse_client_transactions(client, date_from, date_to)
        }
        )
        return all_data

    @classmethod
    def _parse_client_transactions(cls, client, date_from=None, date_to=None):
        transactions_list = []
        delimiter = '+'
        net_cash = 0
        transactions_queryset = client.transactions
        if date_from:
            transactions_queryset = transactions_queryset.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
        transactions_queryset = transactions_queryset.all()
        if transactions_queryset.exists():
            for transaction in transactions_queryset:
                if transaction.payment_type == 1:
                    debit = transaction.amount
                    credit=0
                    net_cash += transaction.amount
                    delimiter = '+'
                else:
                    delimiter = '-'
                    credit = transaction.amount
                    debit=0
                    net_cash -= transaction.amount

                inner_description = transaction.description if transaction.description else ''
                transactions_list.append(
                [
                    str(net_cash),
                    '- '+  str(credit),
                    '+ '+ str(debit),
                    str(transaction.issued_at),
                    f'{delimiter} {transaction.type_tranasction} {inner_description}'

                ])
            return transactions_list



def headers_letters_list():
    return ['A' ,'B' ,'C' ,'D' ,'E' ,'F' ,'G' ,'H' ,'I' ,'J','K' ,'L' ,'M' ,'N' ,'O' ,'P' ,'Q' ,'R' ,'S' ,'T' ,'V' ,'X' ,'Y' ,'Z']

def make_xls_headers(work_sheet, sheet_headers: List, headers_format, merge_from=1, merge_to=2):
    headers_letters = headers_letters_list()
    headers_letters_index = 2
    first_index_merge_from = headers_letters[0]+str(merge_from) +'-'+headers_letters[0]+str(merge_to)
    first_index_merge_to = headers_letters[1]+str(merge_to)
    work_sheet.merge_range(first_index_merge_from+':'+first_index_merge_to,  sheet_headers.pop(), cell_format=headers_format)
    loop_no=len(sheet_headers)
    for loop_row in range(loop_no):
        first_index_merge_from = headers_letters[headers_letters_index]+str(merge_from) +'-'+headers_letters[headers_letters_index]+str(merge_to)
        first_index_merge_to = headers_letters[headers_letters_index+1]+str(merge_to)
        work_sheet.merge_range(first_index_merge_from+":"+first_index_merge_to,  sheet_headers.pop(), cell_format=headers_format)
        headers_letters_index+=2

    
def     make_xls_data(work_sheet, data, data_fields_names,data_format):
    headers_letters = headers_letters_list()
    loop = 0
    for row in data:
        index = 0
        loop=loop
        for field_name in data_fields_names:
            col_name = headers_letters[index]
            work_sheet.merge_range(col_name+str(loop+3)+':'+headers_letters[index+1]+str(loop+3), str(getattr(row, field_name)) if getattr(row, field_name) else '', cell_format=data_format)
            index+=2
        loop+=1


class PaymentTransactionHelper:
    @classmethod
    def pdf(cls, transaction, path=None):
        cosumer = cls.get_consumer_type(transaction)
        context_data = cls._preapare_data_pdf(transaction, cosumer)
        template_path='payment/transactions/pdf.html'        
      
        if path:
            template_path = path

        template = cls._prepare_template(context_data, template_path)

        date = str_to_date(datetime.today().strftime('%Y-%m-%d'))
        filename = 'Transactions for {}'.format(date)

        # responese = HttpResponse(content_type='application/pdf; charset=UTF-8')
        responese = HttpResponse(content_type='text/html; charset=UTF-8')
        # responese['Content-Disposition'] = 'inline; filename={}.pdf'.format(filename)

        # pisa.CreatePDF(
        #     template,
        #     dest=responese,
        #     encoding='UTF-8'
        # )

        return HttpResponse(template)

    @classmethod
    def _prepare_template(cls, data, path='payment/transactions/pdf.html'):
        return render_to_string(template_name=path, context=data)

    @classmethod
    def _preapare_data_pdf(cls, transaction, consumer):
        cols =  [
            _('ID'),
            _('supplier' if consumer == 'supplier'else "Client"),
            _('AMOUNT'),
            _('DESCRIPTION'),
            _('TYPE'),
            _('ISSUED AT')
        ]   
        des = transaction.description if transaction.description else ' '
        des+=' ' + transaction.type_tranasction
        values = []
        values.append(transaction.id)
        values.append(str(getattr(transaction, consumer)))
        values.append(f'{transaction.amount} {_(get_currency(transaction.currency))} ')
        values.append( des )
        values.append( _(get_payment_type(transaction.payment_type)))
        values.append(transaction.issued_at)
        return {
            'values': values,
            'cols': cols,
            'title': _('transaction'),  
            'print':_('print'),
            'cancel':_('cancel'),
        }
    
    @classmethod
    def get_consumer(cls, transaction):
        cosumer  = None
        try :
            cosumer = transaction.client
        except AttributeError:
            cosumer = transaction.supplier
        finally:
            return cosumer

    @classmethod
    def get_consumer_type(cls, transaction):
        cosumer_type  = ''
        try :
            transaction.client
            cosumer_type = 'client'
        except AttributeError:
            transaction.supplier
            cosumer_type = 'supplier'
        finally:
            return cosumer_type


def admin_download_transaction_pdf(obj, consumer,request=None,response=None ):
        consumer_model = getattr(obj,consumer)
        unchanged_customer_str_  = consumer
        
        des = ' - '+ str(obj.description) if obj.description else ' '
        
        main_data = [
            [_("date of transaction"), consumer_model.transactions.last().issued_at.strftime('%d-%m-%Y %H:%I')],
            [_("day of transaction"), consumer_model.transactions.last().issued_at_day()],
            [_('id of transaction'), obj.id ],
            [_(consumer), consumer_model],
            [_('amount'), obj.amount_currency()],
            ['', modified_num2words(obj.amount)],
            [_('that is for'), str(obj.type_tranasction) + des],
            [_('notes'), '.............................................' * 2],
        ]
        modified_consumer = _(' mentioned supplier ')  if consumer == 'supplier' else _(' mentioned client ')
                    
        balance_str_portion = _("balance required from ")
        required_balance = consumer_model.parsed_get_credit()
        if obj.payment_type == 1:
            required_balance = consumer_model.parsed_get_debit()
            balance_str_portion = _("balance of ")
            consumer= modified_consumer

        last_data =[
            [balance_str_portion+ ' '+_(consumer), required_balance,],
        ]
        
        file_name = _('recipet for reciving') + ' '
        file_name+= _('money - checks') if obj.type_tranasction.id == 2 or obj.type_tranasction.id == 3 else _(str(obj.type_tranasction))

        context = {
            'main_data': main_data,
            'last_data':last_data,
            'times': range(2),
            'title': file_name,
            'app_name': _('closthes shop el wensh'),
            'date': obj.issued_at.strftime('%d-%m-%Y %H:%I ') ,
            'branch': _('Main brnach'),
            'print':  _('print'),
            'cancel': _('cancel'),
            'consumer': _(consumer),
            'issued_by_str':_('issued by'),
            'issued_by':str(obj.issued_by),
            'label_of_transaction':file_name ,
            'copy_label': _('copy for ') + _(unchanged_customer_str_),
            'time_of_print_str': _('time of print'),
            'time_of_print': timezone.now().strftime('%d-%m-%Y %H:%I '),
        }

        template = render_to_string('payment/imposit/pdf.html', context)
        # pisa.CreatePDF(
        #     template,
        #     dest=response,
        #     encoding='UTF-8',
        #     link_callback=XPDF.link_callback,
        #     default_css=default_css
        # )    

        # embded_js='<script>  window.open("/admin", "width=300,height=300") </script>'     
        return  HttpResponse(template)

def admin_supplier_download_transaction_pdf(obj, request=None,response=None , consumer='supplier'):
    return admin_download_transaction_pdf(obj, request=request,response=response, consumer=consumer)

def admin_client_download_transaction_pdf(obj, request=None,response=None , consumer='client'):
    return admin_download_transaction_pdf(obj, request=request,response=response, consumer=consumer)



class XPDF:
        @classmethod
        def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path


class Js:
    @classmethod
    def print(cls, url, options):
        width= options.get('width','500px')
        height= options.get('height','500px')
        # with open('print_browser.js', 'r') as js_file:
        js = f"<script>window.open({url}, )</script>"
        
        return HttpResponse()
    
class Amount:
    @classmethod
    def parse_currency(cls, amount):
        return cls.parse(amount) + _("egp") 
        
    @classmethod
    def parse(cls, amount):
        return " {:,.2f}  ".format(amount) 

    @classmethod
    def parse_with_label(cls, amount):
        if amount > 0:
            output = cls.parse(amount) + _('debit') 
        else:
            output = cls.parse(amount) + _('credit') 
        return output
    
    
    
class TempSupplier:
    @classmethod
    def _get_data(cls, suppliers):
        all_data = []
        for supplier in suppliers:
            all_data.append(
            {
                'supplier':supplier,
                'transactions_list':cls._parse_supplier_transactions(supplier)
            }
            )
        return all_data

    @classmethod
    def new_account_statment_pdf(cls, supplier, date_from=None, date_to=None):
        supplier_name = str(supplier)
        data = []
        total = 0
        supplier_transactions = supplier.transactions.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
       
        total_transaction_count  = math.ceil(supplier_transactions.count()  / 25)
       
        cols = [
                [
                    'debit',
                    _('Debit'),
                ],
                [
                    'credit',
                    _('Credit'),
                ], 
                [
                    'description',
                    _('Description'),
                ],
                [
                    'transaction',
                    _('transaction type'),
                ],
                [
                    'issued',
                    _('transaction date'),
                ],
                [
                        'id_transaction',
                        _('id of transaction'),
                ],
            ]
        index = 1
        for transaction in supplier_transactions.all():
            credit = '-'
            debit = '-'

            if transaction.payment_type == 1:
                debit = transaction.amount
                total += debit
            else:
                credit = transaction.amount
                total -= credit
            des = str(transaction.type_tranasction)
            des += '' if not transaction.description else ' - '+ transaction.description
            
            data.append([
                Amount.parse(debit) if not debit == '-' else debit,
                Amount.parse(credit) if not credit == '-' else credit,
                des,
                str(get_payment_type(transaction.payment_type)),
                datetime.strftime(transaction.issued_at, '%Y-%m-%d   %I:%M %p'),
                index
            ])
            index+=1
            
        today = timezone.now()

        context = {
            'cols': cols,
            'transactions': data,
            'account_statment':_('account statment for supplier : '),
            'title': _('account statments to ') +' '+ naturaltime(today),
            'app_name': _('closthes shop el wensh'),
            'phone': '011114548878',
            'date': today   ,
            'branch': _('Main brnach'),
            'address': _("shubra st"),
            'side_info': _('transactions which have been done till') +' : '+ str(today.date()),
            # 'user': request.user,
            'at_date': today.strftime("%Y-%m-%d") ,
            'at_time': today.strftime("%H:%I") ,
            'accountant': _('accountant'),
            'authorize': _("authorize"),
            'reciver': _('reciver'),
            'total': Amount.parse_with_label(total) ,
            'total_str': _('total'),
            'next_page': format_html('<pdf:nextpage>'),
            'total_transaction_count': total_transaction_count,
            'page_number': 1,
            'supplier': supplier_name
        }

        template = render_to_string('supplier/statment/pdf.html', context)
        file_name = 'templates/supplier/statment/output.pdf'
        new_file_name = f'suppliers/{supplier_name}.pdf' 
        result_file = open(file_name, "wb")
        
        pisa.CreatePDF(
            src=template,
            dest=result_file,
            encoding='utf-8'
        ).addPageCount()
        
        shutil.copy2(file_name, new_file_name)

        return new_file_name
    
        
    @classmethod
    def new_get_data(cls, supplier, date_from=None, date_to=None):
        all_data = []
        all_data.append(
        {
            'supplier':supplier,
            'transactions_list':cls._parse_supplier_transactions(supplier, date_from, date_to)
        }
        )
        return all_data

    @classmethod
    def _parse_supplier_transactions(cls, supplier, date_from=None, date_to=None):
        transactions_list = []
        delimiter = '+'
        net_cash = 0
        transactions_queryset = supplier.transactions
        if date_from:
            transactions_queryset = transactions_queryset.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
        transactions_queryset = transactions_queryset.all()
        if transactions_queryset.exists():
            for transaction in transactions_queryset:
                if transaction.payment_type == 1:
                    debit = transaction.amount
                    credit=0
                    net_cash += transaction.amount
                    delimiter = '+'
                else:
                    delimiter = '-'
                    credit = transaction.amount
                    debit=0
                    net_cash -= transaction.amount

                inner_description = transaction.description if transaction.description else ''
                transactions_list.append(
                [
                    str(net_cash),
                    '- '+  str(credit),
                    '+ '+ str(debit),
                    str(transaction.issued_at),
                    f'{delimiter} {transaction.type_tranasction} {inner_description}'

                ])
            return transactions_list

class CommonMethods():
    @classmethod
    def export_as_xls(cls, request, queryset, consumer_str='supplier'):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        consumer_str = 'client' if not consumer_str == 'supplier' else consumer_str
        xls = xlsxwriter.Workbook(response)
        work_sheet = xls.add_worksheet()
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
        sheet_headers = [
            _('issued_at'),
            _('type_tranasction'),
            _('amount'),
            _('description'),
            _('id'),
            _(consumer_str),
        ]
        qs_values = queryset.order_by('-id').all()
        make_xls_headers(work_sheet, sheet_headers, headers_format)
        data_fields_names = [
            consumer_str,
            'id',
            'description',
            'amount',
            'type_tranasction',
            'issued_at',
        ]
        make_xls_data(work_sheet, qs_values, data_fields_names, data_format)
        xls.close()
        return response
    export_as_xls.short_description = ugettext_lazy("Export Selected")


    @classmethod
    def account_statment_pdf(cls, request, date_from, date_to, consumer_obj):
        neddle = cls.get_template_by_class_name(consumer_obj)
        template =  f'{neddle}/statment/pdf.html'
        data= cls.account_statment_data(date_from, date_to, consumer_obj)
        if not data:
            return HttpResponse(_('There are no transactions for that date'))

        tepmlate_to_str = cls.template_render_to_string(template, data, request)
        
        response =  HttpResponse(tepmlate_to_str)
        return  response
    
    @classmethod
    def template_render_to_string(cls, template_path, data, request):
        return render_to_string(template_path, context=data, request=request)   
    
    @classmethod
    def get_template_by_class_name(cls, obj):
        return obj.__class__.__name__.lower()

    @classmethod
    def account_statment_data(cls, date_from, date_to, cosumer_obj):
        date_from = str_to_date(date_from)
        date_to = str_to_date(date_to)
        transactions = cosumer_obj.transactions.filter(issued_at__gte=date_from).filter(issued_at__lte=date_to)
        if not transactions.exists():
            return {}
        
        transactions_data = []
        balance= 0
        credit= 0
        debit= 0
        total_debit = 0
        total_credit = 0
        for transaction in transactions:
            des = str(transaction.type_tranasction)
            des += ' - ' + transaction.description if  transaction.description else ''

            if transaction.payment_type == 1 :
                debit = transaction.amount
                total_debit+=debit
                balance +=int(debit)
                credit=0
            else:
                credit = transaction.amount
                total_credit+=credit
                balance -=int(credit)
                debit = 0

            transactions_data.append([
                transaction.id,
                des,
                transaction.issued_at.strftime('%Y-%m-%d %H:%I '),
                Amount.parse(debit),
                Amount.parse(credit),
                Amount.parse(balance),
                str(transaction.issued_by)
            ])

        transactions_data.append([
                '',
                '',
                '',
                Amount.parse(total_debit),
                Amount.parse(total_credit),
                Amount.parse(balance),
                '',
            ])

        cols = [
        _("id of transaction"),
        _('Description'),
        _("Issued at"),
        _('Debit'),
        _('Credit'),
        _('Blanace'),
        _('Issued by'),
        ]
        today= timezone.now().date()
        time_of_print = today
        today = today.strftime('%Y-%m-%d')
        from_date = transactions.first().issued_at.strftime("%Y-%m-%d") if transactions.first().issued_at else ""
        consumer_str = cosumer_obj.__class__.__name__.lower()
        consumers_str = 'clients' if consumer_str == 'client' else 'suppliers' 
        title = _('account statment') + ' '+ _('for ' +consumers_str)
        
        context = {
            'cols': cols,
            'branch_label': _('the centeral branch'),            
            'transactions': transactions_data,
            'transactions_label': _('account statment for supplier') if consumer_str == 'supplier' else _('account statment for client'),
            'from': _('from'),
            'to': _('to'),
            'print':_('print'),
            'cancel':_('cancel'),
            'total_cost': _('net cost'),
            'title': title,
            'app_name': _('closthes shop el wensh'),
            'phone': '011114548878',
            'account_statment':  _('account statment for supplier') if cosumer_obj.__class__.__name__.lower() == 'supplier' else _('account statment for client') ,
            'date': today   ,
            'branch': _('Main brnach'),
            'address': _("shubra st"),
            'side_info': _('transactions which have been done between')+ str(from_date) + ' : ' + today,
            'accountant': _('accountant'),
            'authorize': _("authorize"),
            'reciver': _('reciver'),
            'total': cosumer_obj.parsed_get_net() ,
            'total_str': _('total'),
            'next_page': format_html('<pdf:nextpage>'),
            'consumer': str(cosumer_obj),
            'time_of_print_str': _('time of print'),
            'time_of_print': time_of_print.strftime("%Y-%m-%d %H:%I "),
        }
        
        return context


    @classmethod
    def generate_daily_tranasctions(cls, transactions, consumer, new_path=''):
        data = []
        total = 0
        total_debit = 0
        total_credit = 0
        for transaction in transactions.all():
            credit = '-'
            debit = '-'
            amount_needlde = transaction.amount
            if transaction.payment_type == 1:
                debit = transaction.parsed_amount()
                total_debit += amount_needlde
            else:
                credit = transaction.parsed_amount()
                total_credit += amount_needlde
            des = ' ' if not transaction.description else ' - '+transaction.description

            total = total_credit -  total_debit 
            
            data.append([
                transaction.id,
                debit,
                credit,
                str(getattr(transaction, consumer)),
                str(transaction.type_tranasction)+des,
                str(transaction.issued_by),
            ])
        data.append([
                '',
                Amount.parse(total_debit),
                Amount.parse(total_credit),
                Amount.parse(total_credit - total_debit),
                '',
                '',
        ])
        
        cols = [
                _('id of transaction'),
                _('Debit'),
                _('Credit'),
                _(consumer.capitalize()),
                _('Description'),
                _('Issued by')
        ]
        today = timezone.now()
        time_str = transactions.last().issued_at.strftime('%Y-%m-%d ')
        title = 'daily transactions for clients' if consumer == 'client' else  'daily transactions for suppliers'
        context = {
            'cols': cols,
            'transactions': data,
            'title': _(title) ,
            'app_name': _('closthes shop el wensh'),
            'date': today.date().strftime('%Y-%m-%d'),
            'print_date': _('date of printing')+' '+str(today.date().strftime('%Y-%m-%d')),
            'branch': _('Main brnach'),
            'side_info': _('transactions which have been done till') +': '+ str(time_str),
            'at': today.strftime('%Y-%m-%d'),
            'reciver': _('reciver'),
            'accountant': _('accountant'),
            'authorize': _("authorize"),
            'print': _('print'),
            'cancel': _('cancel'),
            'total':  Amount.parse_with_label(total) ,
            'total_str': '',
            'time_of_print_str': _('time of print'),
            'time_of_print': timezone.now().strftime('%Y-%m-%d %H:%I'),

        }
        template = render_to_string(f'{consumer}/daily_transactions/pdf.html', context)

        if new_path:
            template = render_to_string(new_path, context)

        return HttpResponse(template)
    
    @classmethod 
    def make_peroid_close(cls, transactions, consumer):
        consumer_str = cls.get_object_name_lower(consumer)

        net = consumer.prepare_net()
        consumer_debit = consumer.get_debit()
        consumer_credit = consumer.get_credit()
        debit_transactions_count  =  transactions.filter(payment_type=1).count()
        credit_transactions_count =  transactions.filter(payment_type=2).count()
        day = timezone.now()
        from_date = consumer.created_at
        delimter = ''  if net > 0 else '-'
        # net = Amount.parse(net)
            
        
        cls.create_closing_period(
            cash=net,
            delimter=delimter,
            day=from_date,
            consumer=consumer
        )

        last_closing_peroid = cls.get_last_closing_period(consumer)
        if last_closing_peroid:
            net = last_closing_peroid.cash
            from_date = last_closing_peroid.day
            delimter = last_closing_peroid.delimter
        
        page_label = _('closing a period for') +' '+ _(consumer_str)
        context = {
            'fields':
            [
                [_('debit'),  Amount.parse(consumer_debit)],
                [_('credit'), Amount.parse(consumer_credit)],
                [_('net'), str(net)+' '+delimter],
                [_(''),  modified_num2words(abs(consumer.prepare_net()) )   ],
                [_('debit no'), debit_transactions_count],
                [_('credit no'), credit_transactions_count],
            ],
            consumer_str: consumer,
            'page_heading': _('clothes shop'),
            'page_label': page_label,
            'day_label': _('closing day'),
            'address': _(' El-teraa st,shubra'),
            'main_app_label': _('closthes shop el wensh'),
            'main_branch': _('the centeral branch'),
            'from_day': from_date,
            'day': day.date().strftime('%Y-%m-%d'),
            'time': day.time().strftime('%H:%I'),
            'last_cash': net ,
            'from': _('from'),
            'to': _('to'),
            'phone': '012345678',
            'old_cash': _('old balance'),
            'title':_('Peroid Close'),
            'print':_('print'),
            'cancel':_('cancel'),
           "signitures":[
            _('accountant'),
            _('reciver'),
            _("authorize"),
            ]
        }     
        template = render_to_string(f'{consumer_str}/period_close/pdf.html', context)

        return HttpResponse(template)   
    
    @classmethod
    def get_object_name_lower(cls, obj):
        return obj.__class__.__name__.lower()

    @classmethod
    def create_closing_period(cls, **data):
        cash = data.get('cash')
        delimter = data.get('delimter')
        day = data.get('day')
        consumer = data.get('consumer')

        if cls.get_object_name_lower(consumer) == 'supplier':
            ClosingPeriod.objects.create(
                supplier   = consumer,
                cash     = abs(cash),
                day      = day,
                delimter = delimter
            )
        else:
            ClosingPeriod.objects.create(
                client   = consumer,
                cash     = abs(cash),
                day      = day,
                delimter = delimter
            )

    @classmethod
    def check_closing_peroid_exists(cls, consumer):
        return ClosingPeriod.objects.filter(
            Q(supplier= consumer.id) | Q(client=consumer.id)
        ).exists()


    @classmethod
    def get_last_closing_period(cls, consumer):
        if cls.check_closing_peroid_exists(consumer):
            return ClosingPeriod.objects.filter(Q(supplier=consumer.id) | Q(client=consumer.id)).last()
            