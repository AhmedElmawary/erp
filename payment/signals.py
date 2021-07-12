from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from payment.models import (
        SupplierPaymentTransaction,
        ClientPaymentTransaction,
        PaymentTransactionType,
    )

from client.models import   Client
from supplier.models import Supplier
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http.response import HttpResponse

# @receiver(post_save, sender=ClientPaymentTransaction)
def process_client_deposite(sender, **kwargs):
    template_name = 'payment/deposite/pdf.html'
    data = { 'fields': 
                    [
                    {
                    'field': 'field',
                    'value': 'value',
                    },
                    {
                        'field': 'field2',
                    
                        'value': 'value2',
                    }

                    ]
            }
        
    
    template = render_to_string(template_name, data)
    file_name = 'deposite'
    # response = HttpResponse(content_type='application/pdf')
    response = HttpResponse(content_type='text/html')
    # response['Content-Disposition'] = f'attachment; filename={file_name}.pdf'
    # pisa.CreatePDF(
    #     template,
    #     response,
    #     encoding='utf-8'
    # )
    
    return HttpResponse(template)

# @receiver(post_save, sender=SupplierPaymentTransaction)
def process_client_deposite(sender, **kwargs):
    print(sender)