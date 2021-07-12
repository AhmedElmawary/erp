from _helpers.tests import SUPPLIER, SUPPLIER_TRANSACTIONS
from payment.models import PaymentTransactionType, SupplierPaymentTransaction
from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser
from django.utils.translation import ugettext_lazy as _
from supplier.models import Supplier

class Command(BaseCommand):
    help = 'seeding transactions types'
    def add_arguments(self, parser: CommandParser) -> None:
            pass

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        transactions_types = [
           {
               'name' : _('purchases invoice'),
               'transaction_for': 1,
               'for_supplier': True
           },
           {
               'name' : _('deposite for account'),
               'transaction_for': 2,
               'for_supplier': True
           },{
               'name' : _('deposite from account'),
               'transaction_for': 1,
               'for_client': True
           },{
               'name' : _('refund inovice'),
               'transaction_for': 1,
               'for_client': True
           },{
               'name' : _('sales'),
               'transaction_for': 2,
               'for_client': True
           },{
               'name' : _('refund  inovice'),
               'transaction_for': 2,
               'for_supplier': True
           }
           
        ] 
        
        for row in transactions_types:
            try:
                PaymentTransactionType.objects.create(
                    name=row['name'],
                    transaction_for=row['transaction_for'],
                    for_supplier=row.get('for_supplier', False),
                    for_client=row.get('for_client', False),
                )
                self.stdout.write(self.style.SUCCESS(f'{row["name"]} types migrated successfully'))
            except:
                self.stderr.write(self.style.ERROR(f'{row["name"]} types couldn\'t be migrated'))
