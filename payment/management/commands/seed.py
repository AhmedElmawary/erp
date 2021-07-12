from _helpers.tests import SUPPLIER, SUPPLIER_TRANSACTIONS
from payment.models import SupplierPaymentTransaction
from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser
from django.utils.translation import ugettext_lazy as _
from supplier.models import Supplier

class Command(BaseCommand):
    help = 'seeding  for supplier transactions'
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('supplier_id', type=int)
        parser.add_argument('num', type=int)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        limit = options['num']
        if not limit or limit < 0:
            limit = 1

        for row in range(1, limit):
            supplier = Supplier.objects.get(id=options['supplier_id'])
            SUPPLIER_TRANSACTIONS.update({'supplier': supplier})
            transaction = SupplierPaymentTransaction.objects.create(**SUPPLIER_TRANSACTIONS)
            supplier.transactions.add(transaction)
        
        
        self.stdout.write(self.style.SUCCESS(f'{limit} migrated successfully'))